import sqlite3
from pathlib import Path

from anki.models import Card


db_dir = Path.home() / ".anki"
db_dir.mkdir(exist_ok=True)

DB_PATH = db_dir / "words.sqlite3"


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT NOT NULL UNIQUE,
                description TEXT,
                example TEXT DEFAULT '-',
                isImportant INTEGER NOT NULL DEFAULT 0 CHECK (isImportant IN (0, 1)),
                isMuted INTEGER NOT NULL DEFAULT 0 CHECK (isMuted IN (0, 1)),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CHECK (NOT (isImportant = 1 AND isMuted = 1))
            )
            """
        )


def check_word(word: str) -> bool:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT 1
            FROM words
            WHERE word = ?
            LIMIT 1
            """,
            (word,),
        ).fetchone()
    return row is not None


def add_card(card: Card) -> str:
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO words (word, description, example, isImportant, isMuted)
            VALUES (?, ?, ?, ?, ?)
            """,
            (card.word, card.description, card.example, card.isImportant, card.isMuted),
        )
        return "The card has been added successfully"


def edit_card(id: int, card: Card) -> str:
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE words
            SET
                word = COALESCE(?, word),
                description = COALESCE(?, description),
                example = COALESCE(?, example),
                isImportant = COALESCE(?, isImportant),
                isMuted = COALESCE(?, isMuted)
            WHERE id = ?
            """,
            (card.word, card.description, card.example, card.isImportant, card.isMuted, id),
        )
    return "The card has been edited successfully"


def mark_card_as_important(id: int) -> str:
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE words
            SET isImportant = 1, isMuted = 0
            WHERE id = ?
            """,
            (id,),
        )
    return "The card has been marked as important"


def mark_card_as_muted(id: int) -> str:
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE words
            SET isImportant = 0, isMuted = 1
            WHERE id = ?
            """,
            (id,),
        )
    return "The card has been muted"


def get_cards() -> list[dict]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, word, description, example, isImportant, isMuted
            FROM words
            ORDER BY created_at DESC, id DESC
            """
        ).fetchall()
    return [dict(row) for row in rows]


def get_unmuted_cards() -> list[dict]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, word, description, example, isImportant, isMuted
            FROM words
            WHERE isMuted = 0
            ORDER BY created_at DESC, id DESC
            """
        ).fetchall()
    return [dict(row) for row in rows]


def get_important_cards() -> list[dict]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, word, description, example, isImportant, isMuted
            FROM words
            WHERE isImportant = 1
            ORDER BY created_at DESC, id DESC
            """
        ).fetchall()
    return [dict(row) for row in rows]


def get_muted_cards() -> list[dict]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, word, description, example, isImportant, isMuted
            FROM words
            WHERE isMuted = 1
            ORDER BY created_at DESC, id DESC
            """
        ).fetchall()
    return [dict(row) for row in rows]


def remove_card(id: int) -> str:
    with get_connection() as connection:
        connection.execute(
            """
            DELETE FROM words
            WHERE id = ?
            """,
            (id,),
        )
    return "The card has been deleted"


def get_card_by_id(id: int) -> dict | None:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT id, word, description, example, isImportant, isMuted, created_at
            FROM words
            WHERE id = ?
            """,
            (id,),
        ).fetchone()
    return dict(row) if row is not None else None
