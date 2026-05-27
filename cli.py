import readline

from dotenv import load_dotenv

from anki.cards import add_new_card, edit_card_by_id, find_cards, read_card_id, remove_card_by_id, show_card_by_id
from anki.csv_io import export_csv, import_csv, list_csv_files
from anki.daily import reword_daily_word
from anki.db import get_cards, get_important_cards, get_muted_cards
from anki.game import play
from anki.ui import Palette, color, format_card, rainbow_text
from anki.verbformen_parser import format_verbformen_entry, parse_verbformen


load_dotenv()

commands = ["help", "add", "all", "show", "edit", "remove", "quit", "play", "import", "export", "csv", "important", "muted", "find", "clear", "reword"]
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


def remove_cards_from_input(text: str) -> None:
    text = text.strip()
    if not text:
        remove_card_by_id(read_card_id())
        return

    card_ids: set[int] = set()
    for part in text.split(","):
        part = part.strip()
        if not part:
            print(color("Invalid input", Palette.ERROR))
            return

        if "-" in part:
            start_text, end_text = [value.strip() for value in part.split("-", 1)]
            if not start_text.isdigit() or not end_text.isdigit():
                print(color("Invalid input", Palette.ERROR))
                return

            start = int(start_text)
            end = int(end_text)
            card_ids.update(range(min(start, end), max(start, end) + 1))
        elif part.isdigit():
            card_ids.add(int(part))
        else:
            print(color("Invalid input", Palette.ERROR))
            return

    for card_id in sorted(card_ids):
        remove_card_by_id(card_id)


def get_card_id_from_args(args: str) -> int | None:
    args = args.strip()
    if not args:
        return read_card_id()

    if args.isdigit():
        return int(args)

    print(color("Incorrect ID", Palette.ERROR))
    return None


def print_cards(cards: list[dict]) -> None:
    if not cards:
        print(color("No cards yet", Palette.MUTED))
        return

    print()
    for card in cards:
        print(format_card(card))
    print()


def import_csv_with_completion() -> None:
    csv_files = list_csv_files()
    if csv_files:
        print(color("Available CSV files:", Palette.MUTED))
        for file in csv_files:
            print(file)
    else:
        print(color("No CSV files found in ~/.anki", Palette.MUTED))

    set_completion_options(csv_files)
    try:
        import_csv()
    finally:
        set_completion_options(commands)


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
        user_input = input(f"{Palette.PROMPT}Anki> {Palette.RESET}").strip()
        if not user_input:
            continue

        parts = user_input.split(maxsplit=1)
        user_command = parts[0].lower()
        user_args = parts[1] if len(parts) > 1 else ""

        if user_command == "quit":
            break
        elif user_command == "help":
            show_help()
        elif user_command == "clear":
            clear_screen()
        elif user_command == "reword":
            reword_daily()
        elif user_command == "add":
            add_new_card()
        elif user_command == "all":
            print_cards(get_cards())
        elif user_command == "show":
            show_card_by_id(get_card_id_from_args(user_args))
        elif user_command == "edit":
            edit_card_by_id(get_card_id_from_args(user_args))
        elif user_command == "remove":
            remove_cards_from_input(user_args)
        elif user_command == "play":
            play(set_completion_options, commands)
        elif user_command == "import":
            import_csv_with_completion()
        elif user_command == "export":
            export_csv()
        elif user_command == "important":
            print_cards(get_important_cards())
        elif user_command == "muted":
            print_cards(get_muted_cards())
        elif user_command == "csv":
            files = list_csv_files()
            if files:
                for file in files:
                    print(file)
            else:
                print("Files not found.")
        elif user_command == "find":
            find_cards(set_completion_options, commands)
        else:
            print(color("Unknown command. Type 'help' to see available commands.", Palette.ERROR))
