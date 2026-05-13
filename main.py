import readline, csv, os, sqlite3
from dataclasses import dataclass
from thefuzz import fuzz

import deepl
from dotenv import load_dotenv

from colorama import Fore, Style, init
from random import choice, randint

from anki.db import add_card, edit_card, get_card_by_id, get_cards, remove_card, get_important_cards


init(autoreset=True)
load_dotenv() 


commands = ["help", "add", "all", "show", "edit", "remove", "quit", "play", "import", "export", "csv", "important", "find"]
completion_options = commands


class Palette:
    PROMPT = Fore.CYAN
    LABEL = Fore.YELLOW
    VALUE = Fore.WHITE
    SUCCESS = Fore.GREEN
    ERROR = Fore.RED
    MUTED = Fore.LIGHTBLACK_EX
    RESET = Style.RESET_ALL
    PLAY_TEXT = (
        Fore.BLUE,
        Fore.CYAN,
        Fore.MAGENTA,
        Fore.LIGHTBLUE_EX,
        Fore.LIGHTCYAN_EX,
        Fore.LIGHTGREEN_EX,
        Fore.LIGHTMAGENTA_EX,
    )


@dataclass
class Card:
    word: str
    description: str
    example: str
    isImportant: int = 0


def color(text: str, color_code: str) -> str:
    return f"{color_code}{text}{Palette.RESET}"


def rainbow_text(text: str) -> str:
    return "".join(color(char, choice(Palette.PLAY_TEXT)) for char in text)


def format_card(card: dict) -> str:
    return (
        f"{Palette.MUTED}ID:{Palette.RESET} {Palette.VALUE}{card['id']}{Palette.RESET} "
        f"{Palette.MUTED}|{Palette.RESET} {Palette.SUCCESS}{card['word']}{Palette.RESET} "
        f"{Palette.MUTED}|{Palette.RESET} {Palette.VALUE}{card['description']}{Palette.RESET} "
        f"{Palette.MUTED}|{Palette.RESET} {Palette.VALUE}{card['example']}{Palette.RESET}"
        f"{Palette.MUTED}|{Palette.RESET} {Palette.VALUE}{card['isImportant']}{Palette.RESET}"
    )


def completer(text: str, state: int) -> str | None:
    options = [option for option in completion_options if option.startswith(text)]
    if state < len(options):
        return options[state]
    return None


def set_completion_options(options: list[str]) -> None:
    global completion_options
    completion_options = options


def setup_readline() -> None:
    readline.set_completer(completer)
    readline.parse_and_bind("tab: complete")


def ask(prompt: str) -> str:
    return input(f"{Palette.LABEL}{prompt}{Palette.RESET} {Palette.VALUE}")


def add_new_card() -> None:
    word = ask("Enter a word:").strip()
    description = ask("Enter a description:").strip()
    example = ask("Enter an example:").strip()
    important_answer = ask("Mark this card as important?(+, y, 1):").strip().lower()
    isImportant = 0

    if not word:
        print(color("Word cannot be empty", Palette.ERROR))
        return
    elif not description:
        print(color("Description cannot be empty", Palette.ERROR))
        return
    elif not example:
        example = "-"
    if important_answer in ["+", "y", "1"]:
        isImportant = 1
    

    message = add_card(Card(word=word, description=description, example=example, isImportant=isImportant))
    print(color(message, Palette.SUCCESS))

def read_card_id() -> int | None:
    raw_card_id = ask("Enter card id:").strip()
    if raw_card_id.isdigit():
        return int(raw_card_id)

    print(color("Incorrect ID", Palette.ERROR))
    return None


def show_card_by_id(card_id: int | None) -> dict | None:
    if card_id is None:
        return None

    card = get_card_by_id(card_id)
    if card is None:
        print(color("There is no card with that ID", Palette.ERROR))
        return None

    print(format_card(card))
    return card


def remove_card_by_id(card_id: int | None) -> None:
    if card_id is None:
        return

    card = get_card_by_id(card_id)
    if card is None:
        print(color("There is no card with that ID", Palette.ERROR))
        return

    print(f"{Palette.LABEL}Delete this card?{Palette.RESET} {format_card(card)}")
    confirmation = input(f"{Palette.LABEL}y/n:{Palette.RESET} ").strip().lower()
    if confirmation in ("", "y", "yes"):
        print(color(remove_card(card_id), Palette.SUCCESS))
    else:
        print(color("Deletion cancelled", Palette.MUTED))


def edit_card_by_id(card_id: int | None) -> None:
    if card_id is None:
        return

    card = get_card_by_id(card_id)
    if card is None:
        print(color("There is no card with that ID", Palette.ERROR))
        return

    print(format_card(card))
    word = ask(f'Enter a word:{Palette.MUTED}(or press "Enter")').strip() or card["word"]
    description = ask(f'Enter a description:{Palette.MUTED}(or press "Enter")').strip() or card["description"]
    example = ask(f'Enter an example:{Palette.MUTED}(or press "Enter")').strip() or card["example"]
    important_answer = ask(f'Mark this card as important?:{Palette.MUTED}(or press "Enter")').strip() or card["isImportant"]
    isImportant = 0

    if not word:
        print(color("Word cannot be empty", Palette.ERROR))
        return

    if important_answer in ["+", "y", "1", "Y", 1]:
        isImportant = 1

    message = edit_card(card_id, Card(word=word, description=description, example=example, isImportant=isImportant))
    print(color(message, Palette.SUCCESS))

def show_help() -> None:
    print(color("Available commands:", Palette.MUTED))
    for command in commands:
        print(f"  {Palette.SUCCESS}{command}{Palette.RESET}")

def fuzzy_check(user_word: str, correct_word: str) -> int:
    ratio = fuzz.ratio(user_word, correct_word)
    return ratio


def play() -> None:
    cards = get_cards()
    if not cards:
        return
    score = 0
    playing = True
    print(f"{Palette.ERROR}SELECT a game mode:{Palette.LABEL}\n1. word -> translate -> example.\n2. example -> translate -> word.")
    game_mode = input(f"{Palette.VALUE}Enter a number(1-2): ").strip()
    if game_mode not in ["1", "2"]:
        print(f'{Palette.ERROR}Invalid "{game_mode}" input; game start; DEFAULT GAME mode is 1')
        game_mode = "1"
    print(f"{Palette.ERROR}SELECT a card mode:{Palette.LABEL}\n1. all words.\n2. only important words.")
    card_mode = input(f"{Palette.VALUE}Enter a number(1-2): ").strip()
    if card_mode not in ["1", "2"]:
        print(f'{Palette.ERROR}Invalid "{card_mode}" input; game start; DEFAULT CARD mode is 1')
        card_mode = "1"

    if card_mode == "2":
        cards = get_important_cards()
    
    print(f"{Palette.LABEL}Available commands: !stop, !swap, !deepl, '+'")
    while cards and playing:
        random_ = randint(0, len(cards) - 1)
        card = cards.pop(random_) 
        desc = card["description"].lower()
        correct_answer = [word.strip() for word in desc.split(",")]
        
        if game_mode == "1":
            print(color(card["word"], choice(Palette.PLAY_TEXT)))
        else:
            print(color(card["example"], choice(Palette.PLAY_TEXT)))

        while True:
            user_answer = ask("Answer:").strip().lower()

            if user_answer == "!swap":
                if game_mode == "1":
                    print(card["example"])
                else:
                    print(card["word"])
            elif user_answer == "!deepl":
                try:
                    auth_key = os.getenv("DEEPL_API_KEY")
                    deepl_client = deepl.DeepLClient(auth_key)
                    result = deepl_client.translate_text(f"{card['example']}", target_lang="RU")
                    print(result.text)
                except Exception as e:
                    print(f"Error: {e}")

            elif user_answer == "!stop":
                print(f"{Palette.ERROR}Game over")
                playing = False
                break

            else:
                if user_answer in correct_answer or user_answer == desc or user_answer == "+":
                    print(f"{Palette.SUCCESS}Correct\n")
                    score += 1
                else:
                    fuzzy_max = 0
                    for word in correct_answer:
                        fuzzy_ = fuzzy_check(user_answer, word)
                        fuzzy_max = max(fuzzy_max, fuzzy_)
                    if fuzzy_max > 90:
                        print(f"{Palette.LABEL}Your answer seems like correct! But with little mistake. +1\n")
                        score += 1
                    else:
                        print(f'{Palette.ERROR}Incorrect. Correct answer is "{card['description']}" cardID:{card['id']}\n')
                break

    print(color(f"Score: {score}", Palette.LABEL))

def get_unique_filename(base_name, used_files):
    n = 1
    filename = base_name

    if used_files is None:
        return filename

    while f"{filename}.csv" in used_files:
        filename = f"{base_name}({n})"
        n += 1

    return filename

def export_csv():
    base_path = os.path.expanduser("~/.anki")
    os.makedirs(base_path, exist_ok=True)

    cards = get_cards()
    if not cards:
        print("You don't have the words yet")
        return
    used_files = list_csv_files()

    filename = input("Input file name: ").strip() or "deck"

    filename = get_unique_filename(filename, used_files)

    filepath = os.path.join(base_path, filename + ".csv")

    try:
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';')

            for card in cards:
                writer.writerow([card['word'], card['description'], card['example']])

        print(f"Saved: {filepath}")

    except Exception as e:
        print(f"Error: {e}")

def import_csv():
    filename = input("Input file name (deck.csv): ")
    path = os.path.expanduser("~/.anki/" + filename)
    try:
        with open(path, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile, delimiter=';')

            user_import = input("Confirm the import(y/n): ").strip().lower()
            if user_import == "y" or user_import == "":
                for row in reader:
                    if len(row) >= 3:
                        try:
                            add_card(Card(word=row[0], description=row[1], example=row[2]))
                            print(f"{Palette.SUCCESS}The {row[0]} import completed successfully")
                        except sqlite3.IntegrityError as e:
                            if "UNIQUE constraint failed: words.word" in str(e):
                                print(f"{Palette.ERROR}Error: The {row[0]} already exists.")
                            else:
                                print(f"{Palette.ERROR}Error: {e}")
                        except Exception as e:
                            print(f"{Palette.ERROR}Error: {e}")
                    else:
                        print(f"{Palette.ERROR}It seems like {filename} was empty")

    except Exception as e:
        print(f"Error: {e}")

def list_csv_files() -> list[str] | None:
    folder = os.path.expanduser("~/.anki")

    try:
        files = os.listdir(folder)

        csv_files = [f for f in files if f.endswith(".csv")]
        return csv_files

    except FileNotFoundError:
        print("The folder was not found.")
    except Exception as e:
        print(f"Error: {e}")

def find_cards() -> None:
    cards = get_cards()
    if not cards:
        print(color("No cards yet", Palette.MUTED))
        return

    words = [card["word"] for card in cards]
    set_completion_options(words)
    try:
        search_word = ask("Find word:").strip().lower()
    finally:
        set_completion_options(commands)

    if not search_word:
        return

    found_cards = [card for card in cards if search_word in card["word"].lower()]
    if not found_cards:
        print(color("No matching cards found", Palette.MUTED))
        return

    print()
    for card in found_cards:
        print(format_card(card))
    print()

def main() -> None:
    print(rainbow_text("Anki CLI started"))
    setup_readline()

    while True:
        user_input = input(f"{Palette.PROMPT}Anki> {Palette.RESET}").strip().lower()

        if user_input == "quit":
            break
        if user_input == "help":
            show_help()
        elif user_input == "add":
            add_new_card()
        elif user_input == "all":
            cards = get_cards()
            if cards:
                print()
                for card in cards:
                    print(format_card(card))
                print()
        elif user_input == "show":
            show_card_by_id(read_card_id())
        elif user_input == "edit":
            edit_card_by_id(read_card_id())
        elif user_input == "remove":
            remove_card_by_id(read_card_id())
        elif user_input == "play":
            play()
        elif user_input == "import":
            import_csv()
        elif user_input == "export":
            export_csv()
        elif user_input == "important":
            cards = get_important_cards()
            if cards:
                print()
                for card in cards:
                    print(format_card(card))
                print()
        elif user_input == "csv":
            files = list_csv_files()
            if files:
                for file in files:
                    print(file)
            else:
                print("Files not found.")
        elif user_input == "find":
            find_cards()
        elif user_input:
            print(color("Unknown command. Type 'help' to see available commands.", Palette.ERROR))


if __name__ == "__main__":
    main()
