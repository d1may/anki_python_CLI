import readline

from dotenv import load_dotenv

from anki.cards import add_new_card, edit_card_by_id, find_cards, read_card_id, remove_card_by_id, show_card_by_id
from anki.csv_io import export_csv, import_csv, list_csv_files
from anki.daily import reword_daily_word
from anki.db import get_cards, get_important_cards
from anki.game import play
from anki.ui import Palette, color, format_card, rainbow_text
from anki.verbformen_parser import format_verbformen_entry, parse_verbformen


load_dotenv()

commands = ["help", "add", "all", "show", "edit", "remove", "quit", "play", "import", "export", "csv", "important", "find", "clear", "reword"]
completion_options = commands


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


def show_help() -> None:
    print(color("Available commands:", Palette.MUTED))
    for command in commands:
        print(f"  {Palette.SUCCESS}{command}{Palette.RESET}")


def clear_screen() -> None:
    print("\033[2J\033[H", end="")


def reword_daily() -> None:
    word = reword_daily_word()
    if not word:
        print(color("No words found.", Palette.MUTED))
        return

    try:
        entry = parse_verbformen(word, timeout=5)
    except Exception as error:
        print(color(f'Could not parse "{word}": {error}', Palette.ERROR))
        return

    print(color(format_verbformen_entry(entry), Palette.SUCCESS))


def main() -> None:
    print(rainbow_text("Anki CLI started"))
    setup_readline()
    
    while True:
        user_input = input(f"{Palette.PROMPT}Anki> {Palette.RESET}").strip().lower()

        if user_input == "quit":
            break
        if user_input == "help":
            show_help()
        elif user_input == "clear":
            clear_screen()
        elif user_input == "reword":
            reword_daily()
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
            find_cards(set_completion_options, commands)
        elif user_input:
            print(color("Unknown command. Type 'help' to see available commands.", Palette.ERROR))
