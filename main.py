import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from anki.cli import main as cli_main
from anki.daily import get_daily_word
from anki.db import init_db
from anki.ui import Palette, color
from anki.verbformen_parser import format_verbformen_entry, parse_verbformen


def show_daily_word() -> None:
    word = get_daily_word()
    if not word:
        return

    try:
        entry = parse_verbformen(word, timeout=5)
    except Exception as error:
        print(color(f'Could not parse "{word}": {error}', Palette.ERROR))
        return

    print(color(format_verbformen_entry(entry), Palette.SUCCESS))


def main() -> None:
    init_db()
    show_daily_word()
    cli_main()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopping Anki...")
    finally:
        print("Anki has been stopped")
