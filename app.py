from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime
from models.event import Event, Priority
from models.event_manager import EventManager
from models.reminder import ReminderSystem
from database import create_tables, add_event as db_add_event, get_all_events, delete_event as db_delete_event, get_event_by_id
from authentication.auth import get_service, add_event_to_google_calendar, logout_google, TOKEN_FILE
import os

app = Flask(__name__)
app.secret_key = "secret123"
manager = EventManager()
reminder = ReminderSystem(manager)
create_tables()

@app.route("/login_google")
def login_google():
    try:
        service = get_service()
        # ได้ service แล้วสามารถ fetch จาก calendarได้
        session['logged_in'] = True
        return redirect(url_for("index"))
    except Exception as e:
        return f"Authentication Failed: {e}"

@app.route("/logout")
def logout():
    # Clear the session variable
    session.pop('logged_in', None)
    # Delete the token.pickle file
    logout_google() 
    
    return redirect(url_for("index"))

@app.route("/")
def index():
    # โหลดข้อมูลจาก JSON ทุกครั้งที่เปิดหน้า
    manager.load_from_json()
    
    # Check if the token file exists to determine login status
    is_authenticated = os.path.exists(TOKEN_FILE)
    
    return render_template("index.html", 
                           events=manager._events, 
                           logged_in=is_authenticated)

@app.route("/add_event", methods=["GET", "POST"])
def add_event():
    if request.method == "POST":
        # รับค่าจากฟอร์ม
        title = request.form["title"]
        date = datetime.strptime(request.form["date"], "%Y-%m-%d")
        subject = request.form["subject"]
        description = request.form["description"]
        priority = Priority[request.form["priority"]]

        # สร้าง Event ใหม่
        new_event = Event(
            id=len(manager._events) + 1,
            title=title,
            date=date,
            subject=subject,
            description=description,
            priority=priority
        )

        #sync Google calendar 
        calendar_id = None
        try:
            service = get_service()
            calendar_id = add_event_to_google_calendar(   #รับ calendar_id
                service, title,
                date.strftime("%Y-%m-%d"),
                description, subject
            )
        except Exception as e:
            # Don't crash — local save already succeeded
            print(f"Google Calendar sync failed: {e}")

        # calendar_id ให้ Event object
        new_event.set_calendar_id(calendar_id)

        # เพิ่มเข้า EventManager และบันทึก
        manager.add_event(new_event)
        manager.save_to_json()

        # บันทึก event ลง SQLite database
        db_add_event(
            title,
            date.strftime("%Y-%m-%d"),
            subject,
            description,
            priority.name,
            calendar_id
        )

        return redirect(url_for("index"))

    return render_template("add_event.html")

@app.route("/delete_event/<int:event_id>", methods=["POST"])
def delete_event(event_id):
    # ดึง calendar_event_id จาก DB ก่อนลบ
    event = get_event_by_id(event_id)
    gcal_id = event[7] if event else None  # index 7 = calendar_id

    # ถ้า DB ไม่มี ให้ fallback ไปหาใน JSON
if gcal_id is None:
    manager.load_from_json()
    json_event = next((e for e in manager._events if e._id == event_id), None)  # e.id → e._id
    gcal_id = json_event._calendar_id if json_event else None  # ใช้ _calendar_id ด้วย

    #debug
    print(f"DEBUG: event = {event}")     
    print(f"DEBUG: gcal_id = {gcal_id}")  

    # ลบจาก Google Calendar
    if gcal_id:
        try:
            service = get_service()
            service.events().delete(calendarId="primary", eventId=gcal_id).execute()
        except Exception as e:
            print(f"Google Calendar delete failed: {e}")

    #delete locally
    manager.load_from_json()
    manager.remove_event(event_id)
    manager.save_to_json()
    db_delete_event(event_id)
    return redirect(url_for("index"))

@app.route("/db_events")
def db_events():
    events = get_all_events()
    return {"events": events}

@app.route("/stats")
def stats():
    analysis = reminder.analyze_events()
    reminders = reminder.send_reminder()
    chart = reminder.generate_calendar_view()
    return render_template("stats.html",
                           analysis=analysis,
                           reminders=reminders,
                           chart=chart)


if __name__ == "__main__":
    app.run(debug=True)