from random import choice, randint
from collections.abc import Callable

from thefuzz import fuzz

from anki.db import (
    get_cards,
    get_important_cards,
    get_muted_cards,
    get_unmuted_cards,
    mark_card_as_important,
    mark_card_as_muted,
)
from anki.deepl_tr import deepl_translate
from anki.ui import Palette, ask, color


def fuzzy_check(user_word: str, correct_word: str) -> int:
    ratio = fuzz.ratio(user_word, correct_word)
    return ratio


GAME_COMMANDS = ["!stop", "!swap", "!deepl", "!mute", "!important", "+"]


def play(set_completion_options: Callable[[list[str]], None] | None = None, default_completion_options: list[str] | None = None) -> None:
    score = 0
    playing = True

    if set_completion_options is not None:
        set_completion_options(GAME_COMMANDS)

    try:
        print(f"{Palette.ERROR}SELECT a game mode:{Palette.LABEL}\n1. word -> translate -> example.\n2. example -> translate -> word.")
        game_mode = input(f"{Palette.VALUE}Enter a number(1-2): ").strip()
        if game_mode not in ["1", "2"]:
            print(f'{Palette.ERROR}Invalid "{game_mode}" input; game start; DEFAULT GAME mode is 1')
            game_mode = "1"

        print(f"{Palette.ERROR}SELECT order mode:{Palette.LABEL}\n1. Random\n2. Newest -> Oldest.\n3. Oldest -> Newest.")
        order_mode = input(f"{Palette.VALUE}Enter a number(1-3): ").strip()
        if order_mode not in ["1", "2", "3"]:
            print(f'{Palette.ERROR}Invalid "{order_mode}" input; game start; DEFAULT order mode is 1')
            order_mode = "1"

        print(
            f"{Palette.ERROR}SELECT a card mode:{Palette.LABEL}\n"
            "1. all words without muted.\n"
            "2. only important words.\n"
            "3. only muted words.\n"
            "4. all words including muted."
        )
        card_mode = input(f"{Palette.VALUE}Enter a number(1-4): ").strip()
        if card_mode not in ["1", "2", "3", "4"]:
            print(f'{Palette.ERROR}Invalid "{card_mode}" input; game start; DEFAULT CARD mode is 1')
            card_mode = "1"

        if card_mode == "1":
            cards = get_unmuted_cards()
            if not cards:
                print(color("No unmuted cards found", Palette.MUTED))
                return
        elif card_mode == "2":
            cards = get_important_cards()
            if not cards:
                print(color("No important cards found", Palette.MUTED))
                return
        elif card_mode == "3":
            cards = get_muted_cards()
            if not cards:
                print(color("No muted cards found", Palette.MUTED))
                return
        else:
            cards = get_cards()
            if not cards:
                print(color("No cards found", Palette.MUTED))
                return

        print(f"{Palette.LABEL}Available commands: {', '.join(GAME_COMMANDS)}")
        while cards and playing:
            card_index = randint(0, len(cards) - 1)
            if order_mode == "2":
                card_index = 0
            elif order_mode == "3":
                card_index = -1
            card = cards.pop(card_index)
            desc = (card["description"] or "").lower()
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
                    print(deepl_translate(card['example']))

                elif user_answer == "!mute":
                    print(color(mark_card_as_muted(card["id"]), Palette.SUCCESS))
                    card["isMuted"] = 1
                    card["isImportant"] = 0

                elif user_answer == "!important":
                    print(color(mark_card_as_important(card["id"]), Palette.SUCCESS))
                    card["isImportant"] = 1
                    card["isMuted"] = 0

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
                            print(f'{Palette.ERROR}Incorrect. Correct answer is "{card["description"]}" cardID:{card["id"]}\n')
                    break

        print(color(f"Score: {score}", Palette.LABEL))
    finally:
        if set_completion_options is not None and default_completion_options is not None:
            set_completion_options(default_completion_options)
