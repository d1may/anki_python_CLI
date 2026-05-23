from collections.abc import Callable

from anki.db import add_card, edit_card, get_card_by_id, get_cards, remove_card
from anki.models import Card
from anki.ui import Palette, ask, color, format_card


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
    important_answer = ask(f'Mark this card as important?:{Palette.MUTED}(or press "Enter")').strip()
    isImportant = card["isImportant"]

    if not word:
        print(color("Word cannot be empty", Palette.ERROR))
        return

    if important_answer in ["+", "y", "1", "Y"]:
        isImportant = 1
    elif important_answer:
        isImportant = 0

    message = edit_card(card_id, Card(word=word, description=description, example=example, isImportant=isImportant))
    print(color(message, Palette.SUCCESS))


def find_cards(set_completion_options: Callable[[list[str]], None], commands: list[str]) -> None:
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
