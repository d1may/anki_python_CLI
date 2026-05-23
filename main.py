from pathlib import Path
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from anki.cli import main as cli_main
from anki.daily import get_daily_card
from anki.ui import Palette, color
from anki.verbformen_parser import format_verbformen_entry, parse_verbformen
from random import choice


def main() -> None:
    words = get_daily_card()
    if words:
        word = choice(words)
        try:
            entry = parse_verbformen(word)
            print(color(format_verbformen_entry(entry), Palette.SUCCESS))
        except Exception as error:
            print(color(f'Could not parse "{word}": {error}', Palette.ERROR))
    cli_main()


if __name__ == "__main__":
    main()
