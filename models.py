from dataclasses import dataclass


@dataclass
class Card:
    word: str
    description: str
    example: str
    isImportant: int = 0
