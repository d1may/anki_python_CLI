import csv
import json
import subprocess
from datetime import date
from pathlib import Path
from random import choice


WORDS_CSV = Path(__file__).with_name("top_1000_german_words.csv")
DAILY_STATE_PATH = Path.home() / ".anki" / "daily_word.json"


def load_words() -> list[str]:
    words: list[str] = []
    try:
        with WORDS_CSV.open(newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                word = row.get("word", "").strip()
                if word:
                    words.append(word)
    except Exception as e:
        print(e)
    return words


def load_daily_state() -> dict | None:
    try:
        with DAILY_STATE_PATH.open() as state_file:
            state = json.load(state_file)
    except FileNotFoundError:
        return None
    except (OSError, json.JSONDecodeError) as error:
        print(f"Could not load daily word state: {error}")
        return None

    if not isinstance(state, dict):
        return None

    saved_date = state.get("date")
    saved_word = state.get("word")
    if not isinstance(saved_date, str) or not isinstance(saved_word, str):
        return None

    return state


def save_daily_state(word: str, day: str | None = None) -> None:
    DAILY_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    state = {
        "date": day or date.today().isoformat(),
        "word": word,
    }

    with DAILY_STATE_PATH.open("w") as state_file:
        json.dump(state, state_file, ensure_ascii=False, indent=2)


def pick_random_word(exclude: set[str] | None = None) -> str | None:
    exclude = exclude or set()
    words = [word for word in load_words() if word not in exclude]
    if not words:
        return None

    return choice(words)


def get_daily_word() -> str | None:
    today = date.today().isoformat()
    state = load_daily_state()

    if state and state["date"] == today:
        return state["word"]

    word = pick_random_word()
    if word is None:
        return None

    save_daily_state(word, today)
    return word


def reword_daily_word() -> str | None:
    current_word = get_daily_word()
    exclude = {current_word} if current_word else set()

    word = pick_random_word(exclude=exclude)
    if word is None:
        return current_word

    save_daily_state(word)
    return word


def send_notification(card: dict) -> None:
    title = f"✦ Word of the day: {card['word']}"
    body = f"Translation: {card['description']}\nExample: {card['example']}"

    try:
        subprocess.run(
            ["notify-send", "--urgency=normal", "--expire-time=10000", title, body],
            check=True
        )
    except FileNotFoundError:
        print("notify-send not found. Install it: sudo apt install libnotify-bin")
    except subprocess.CalledProcessError as e:
        print(f"Notification error: {e}")
