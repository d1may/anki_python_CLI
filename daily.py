import os
import csv
import sys
import subprocess
from pathlib import Path
from random import choice, randint

os.environ.setdefault("DISPLAY", ":0")
os.environ.setdefault("DBUS_SESSION_BUS_ADDRESS", "unix:path=/run/user/1000/bus")

WORDS_CSV = Path(__file__).with_name("top_1000_german_words.csv")


def get_daily_card() -> list[str] | None:
    words = []
    try:
        with WORDS_CSV.open(newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                words.append(row['word'])
    except Exception as e:
        print(e)
    return words


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
