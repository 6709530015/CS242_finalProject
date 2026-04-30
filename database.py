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
            status TEXT NOT NULL,
            calendar_id TEXT  -- for Google calendar
        )
    """)

     # Migration: เพิ่ม column ถ้ายังไม่มี calendar_id (DB เก่า)
    try:
        cursor.execute("ALTER TABLE events ADD COLUMN calendar_id TEXT")
        print("Migration: added calendar_id column")
    except sqlite3.OperationalError:
        pass  # column มีอยู่แล้ว

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


def add_event(title, date, subject, description, priority, calendar_id=None):
    conn = get_connection()
    cursor = conn.cursor()

    status = calculate_status(date)

    cursor.execute("""
        INSERT INTO events (title, date, subject, description, priority, status, calendar_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (title, date, subject, description, priority, status, calendar_id))

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

#สำหรับ Calendar
def get_event_by_id(event_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM events WHERE id = ?", (event_id,))
    event = cursor.fetchone()
    conn.close()
    return event  # tuple: (id, title, date, subject, description, priority, status, calendar_id)