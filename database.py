import sqlite3
from datetime import datetime

DB_NAME = "events.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            date TEXT NOT NULL,
            subject TEXT,
            description TEXT,
            priority TEXT NOT NULL,
            status TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()



def calculate_status(date_str):
    event_date = datetime.strptime(date_str, "%Y-%m-%d")
    today = datetime.now()

    diff = (event_date.date() - today.date()).days

    if diff < 0:
        return "OVERDUE"
    elif diff == 0:
        return "TODAY"
    else:
        return "UPCOMING"


def add_event(title, date, subject, description, priority):
    conn = get_connection()
    cursor = conn.cursor()

    status = calculate_status(date)

    cursor.execute("""
        INSERT INTO events (title, date, subject, description, priority, status)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (title, date, subject, description, priority, status))

    conn.commit()
    conn.close()


def get_all_events():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM events ORDER BY date ASC")
    events = cursor.fetchall()

    conn.close()
    return events


def delete_event(event_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM events WHERE id = ?", (event_id,))

    conn.commit()
    conn.close()