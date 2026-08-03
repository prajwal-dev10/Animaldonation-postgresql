import os
import sys
import sqlite3

# Allow imports from project root
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from app import create_app
from app.extensions import db
from app.models import Animal, Event, Donate

app = create_app()


def get_sqlite_connection():
    sqlite_path = os.path.join(PROJECT_ROOT, "old_users.db")

    conn = sqlite3.connect(sqlite_path)
    conn.row_factory = sqlite3.Row

    return conn


def migrate_animals(cursor):
    print("Migrating animals...")

    rows = cursor.execute("SELECT * FROM animal").fetchall()

    count = 0

    for row in rows:

        if Animal.query.get(row["id"]):
            continue

        animal = Animal(
            id=row["id"],
            catagory=row["catagory"],
            name=row["name"],
            description=row["description"],
            image=row["image"]
        )

        db.session.add(animal)
        count += 1

    db.session.commit()

    print(f"✓ {count} animals imported")


def migrate_events(cursor):
    print("Migrating events...")

    rows = cursor.execute("SELECT * FROM event").fetchall()

    count = 0

    for row in rows:

        if Event.query.get(row["id"]):
            continue

        event = Event(
            id=row["id"],
            eventname=row["eventname"],
            date=row["date"],
            description=row["description"],
            image=row["image"]
        )

        db.session.add(event)
        count += 1

    db.session.commit()

    print(f"✓ {count} events imported")


def migrate_donations(cursor):
    print("Migrating donations...")

    rows = cursor.execute("SELECT * FROM donate").fetchall()

    count = 0

    for row in rows:

        if Donate.query.get(row["id"]):
            continue

        donor = Donate(
            id=row["id"],
            Firstname=row["Firstname"],
            Lastname=row["Lastname"],
            Address=row["Address"],
            Email=row["Email"],
            Image=row["Image"],
            Amount=row["Amount"]
        )

        db.session.add(donor)
        count += 1

    db.session.commit()

    print(f"✓ {count} donations imported")


def main():

    conn = get_sqlite_connection()
    cursor = conn.cursor()

    with app.app_context():

        migrate_animals(cursor)
        migrate_events(cursor)
        migrate_donations(cursor)

    conn.close()

    print("\n===================================")
    print("Migration completed successfully!")
    print("===================================")


if __name__ == "__main__":
    main()