import sqlite3
from pathlib import Path


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
                word TEXT NOT NULL,
                description TEXT,
                example TEXT DEFAULT '-',
                isImportant INTEGER NOT NULL DEFAULT 0 CHECK (isImportant IN (0, 1)),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

def add_card(card: Card) -> str:
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO words (word, description, example, isImportant)
            VALUES (?, ?, ?, ?)
            """,
            (card.word, card.description, card.example, card.isImportant),
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
                isImportant = COALESCE(?, isImportant)
            WHERE id = ?
            """,
            (card.word, card.description, card.example, card.isImportant, id),
        )
    return "The card has been edited successfully"

def get_cards() -> list[dict]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, word, description, example, isImportant
            FROM words
            ORDER BY created_at DESC, id DESC
            """
        ).fetchall()
    return [dict(row) for row in rows]

def get_important_cards() -> list[dict]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, word, description, example, isImportant
            FROM words
            WHERE isImportant = 1
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
            SELECT id, word, description, example, isImportant, created_at
            FROM words
            WHERE id = ?
        """,(id,),).fetchone()
    return dict(row) if row is not None else None


init_db()
