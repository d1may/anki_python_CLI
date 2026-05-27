import csv
import os
import sqlite3

from anki.db import add_card, get_cards
from anki.models import Card
from anki.ui import Palette


def get_unique_filename(base_name, used_files):
    n = 1
    filename = base_name

    if used_files is None:
        return filename

    while f"{filename}.csv" in used_files:
        filename = f"{base_name}({n})"
        n += 1

    return filename


def export_csv():
    base_path = os.path.expanduser("~/.anki")
    os.makedirs(base_path, exist_ok=True)

    cards = get_cards()
    if not cards:
        print("You don't have the words yet")
        return
    used_files = list_csv_files()

    filename = input("Input file name: ").strip() or "deck"

    filename = get_unique_filename(filename, used_files)

    filepath = os.path.join(base_path, filename + ".csv")

    try:
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';')

            for card in cards:
                writer.writerow([card['word'], card['description'], card['example']])

        print(f"Saved: {filepath}")

    except Exception as e:
        print(f"Error: {e}")


def import_csv():
    filename = input("Input file name (deck.csv): ")
    path = os.path.expanduser("~/.anki/" + filename)
    try:
        with open(path, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile, delimiter=';')

            user_import = input("Confirm the import(y/n): ").strip().lower()
            if user_import == "y" or user_import == "":
                for row in reader:
                    if len(row) >= 3:
                        try:
                            add_card(Card(word=row[0], description=row[1], example=row[2]))
                            print(f"{Palette.SUCCESS}The {row[0]} import completed successfully")
                        except sqlite3.IntegrityError as e:
                            if "UNIQUE constraint failed: words.word" in str(e):
                                print(f"{Palette.ERROR}Error: The {row[0]} already exists.")
                            else:
                                print(f"{Palette.ERROR}Error: {e}")
                        except Exception as e:
                            print(f"{Palette.ERROR}Error: {e}")
                    else:
                        print(f"{Palette.ERROR}Invalid CSV row: expected 3 columns")

    except Exception as e:
        print(f"Error: {e}")


def list_csv_files() -> list[str]:
    folder = os.path.expanduser("~/.anki")

    try:
        files = os.listdir(folder)
        return sorted(f for f in files if f.endswith(".csv"))

    except FileNotFoundError:
        print("The folder was not found.")
        return []
    except Exception as e:
        print(f"Error: {e}")
        return []
