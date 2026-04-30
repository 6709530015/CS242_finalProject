import json
from datetime import datetime
from models.event import Event, Priority, Status

class EventManager:
    def __init__(self, storage_file="storage/events.json"):
        self._events = []
        self._storage_file = storage_file

    def add_event(self, event: Event):
        self._events.append(event)

    def remove_event(self, event_id: int):
        self._events = [e for e in self._events if e._id != event_id]

    def update_all_status(self):
        for e in self._events:
            days = e.get_days_until()
            if days < 0:
                e._status = Status.OVERDUE
            elif days == 0:
                e._status = Status.TODAY
            else:
                e._status = Status.UPCOMING

    def save_to_json(self):
        with open(self._storage_file, "w") as f:
            json.dump([e.__dict__ for e in self._events], f, default=str)

    def load_from_json(self):
        try:
            with open(self._storage_file, "r") as f:
                content = f.read().strip()
                if not content:          # ไฟล์ว่างเปล่า
                    self._events = []
                    return
                data = json.loads(content)

            self._events = []
            for d in data:
                event = Event(
                    id=d["_id"],
                    title=d["_title"],
                    date=datetime.fromisoformat(d["_date"]),
                    subject=d["_subject"],
                    description=d["_description"],
                    priority=Priority[d["_priority"].split(".")[-1]] if isinstance(d["_priority"], str)
                              else Priority(d["_priority"]),
                    calendar_id=d.get("_calendar_id")
                )
                event._status = Status[d["_status"].split(".")[-1]] if isinstance(d["_status"], str) \
                                 else Status(d["_status"])
                self._events.append(event)

        except (FileNotFoundError, json.JSONDecodeError):
            # ไฟล์ยังไม่มี หรืออ่านไม่ได้ → เริ่มด้วย list ว่าง
            self._events = []