import argparse
import csv
import getpass
import json
import re

import Anki
import Conf
import Pomodoro
import Rows

import Safaribooks
import ACM


def interactive_login(session):
    while not session.bearer:
        while True:
            try:
                password = getpass.getpass("Password: ")
                break
            except KeyboardInterrupt:
                print("")

        try:
            session.login(user, password)
        except ConnectionError:
            print("Login failed, try again")
            continue
    print("Login successful!")


def process_csv(csv_data):
    placeholder = "- "
    processed_data = [re.sub(r",\s", placeholder, row, count=1) for row in csv_data]
    file = csv.reader(csv_data, delimiter=",", quotechar='"')
    try:
        next(file)
    except csv.Error:
        exit()
    rows = Rows.Rows()
    for row in file:
        if row:
            row = [x.strip() for x in row]
            if len(row) != 9:
                print(row)
                raise ValueError("Row does not have 9 columns")
            for note in Rows.make_record(row):
                rows.add_row(note)
    return rows


def main():
    parser = argparse.ArgumentParser(description="Incremodoro")
    parser.add_argument(
        "--notes",
        help="Review all empty notes.",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--bookmarks",
        help="Review all bookmarks.",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--match",
        metavar="pattern",
        type=str,
        help="Find highlights matching pattern",
        default="",
    )

    parser.add_argument(
        "--delete",
        help="Delete highlights after they are put in flashcard deck",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--dempty",
        help="Delete empty highlights that match pattern",
        action="store_true",
        default=False,
    )

    results = parser.parse_args()
    try:
        f = open(".credentials.json")
        cred = json.load(f)
        user = cred["user"]
        password = cred["password"]
    except:
        user = input("Username: ")
        password = ""
    if "acm" in user:
        user = user.split("@")[0]
        session = ACM.Session()
    else:
        session = Safaribooks.Session()
    session.interactive_login(user, password)
    csv = session.download_csv()
    print(csv)
    csv_data = process_csv(csv)
    bookmarks = csv_data.bookmarks
    review = csv_data.empty_highlights + csv_data.missing_tags
    highlights = csv_data.highlights
    metadata = session.download_metadata(highlights)
    for highlight in highlights:
        highlight.author = ", ".join(
            a["name"] for a in metadata[highlight.isbn]["authors"]
        )
    conf = Conf.Configuration("conf.yml")
    deck = Anki.Deck(**conf.conf)
    deck.download_media(highlights)
    deck.add_cards(highlights)
    deck.compile_deck()
    if results.dempty:
        for h in csv_data.empty_highlights:
            session.delete_highlight(h, results.match)
    if results.delete:
        for h in highlights:
            session.delete_highlight(h)
    if results.delete and results.bookmarks:
        for b in bookmarks:
            session.delete_highlight(b)
    pomodoro = Pomodoro.Pomodoro()
    if results.notes:
        pomodoro.review(review, results.match)

    if results.bookmarks and not results.delete:
        pomodoro.review(bookmarks, results.match)


if __name__ == "__main__":
    main()
