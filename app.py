from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
from models.event import Event, Priority
from models.event_manager import EventManager

app = Flask(__name__)
manager = EventManager()

@app.route("/")
def index():
    # โหลดข้อมูลจาก JSON ทุกครั้งที่เปิดหน้า
    manager.load_from_json()
    return render_template("index.html", events=manager._events)

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

        # เพิ่มเข้า EventManager และบันทึก
        manager.add_event(new_event)
        manager.save_to_json()

        return redirect(url_for("index"))

    return render_template("add_event.html")

if __name__ == "__main__":
    app.run(debug=True)
