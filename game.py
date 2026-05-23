from random import choice, randint

import deepl
from thefuzz import fuzz

from anki.db import get_cards, get_important_cards
from anki.deepl_tr import deepl_translate
from anki.ui import Palette, ask, color


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

    print(f"{Palette.ERROR}SELECT a order mode:{Palette.LABEL}\n1. Random\n2. Newest -> Oldest.\n3. Oldest -> Newest.")
    order_mode = input(f"{Palette.VALUE}Enter a number(1-3): ").strip()
    if order_mode not in ["1", "2", "3"]:
        print(f'{Palette.ERROR}Invalid "{order_mode}" input; game start; DEFAULT GAME mode is 1')
        order_mode = "1"

    print(f"{Palette.ERROR}SELECT a card mode:{Palette.LABEL}\n1. all words.\n2. only important words.")
    card_mode = input(f"{Palette.VALUE}Enter a number(1-2): ").strip()
    if card_mode not in ["1", "2"]:
        print(f'{Palette.ERROR}Invalid "{card_mode}" input; game start; DEFAULT CARD mode is 1')
        card_mode = "1"
    elif card_mode == "2":
        cards = get_important_cards()

    print(f"{Palette.LABEL}Available commands: !stop, !swap, !deepl, '+'")
    while cards and playing:
        card_index = randint(0, len(cards) - 1)
        if order_mode == "2":
            card_index = 0
        elif order_mode == "3":
            card_index = -1
        card = cards.pop(card_index)
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
                print(deepl_translate(card['example']))

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
