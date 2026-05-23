from random import choice

from colorama import Fore, Style, init


init(autoreset=True)


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


def ask(prompt: str) -> str:
    return input(f"{Palette.LABEL}{prompt}{Palette.RESET} {Palette.VALUE}")
