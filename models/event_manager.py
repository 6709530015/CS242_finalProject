import json
from models.event import Event

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
        with open(self._storage_file, "r") as f:
            data = json.load(f)
            # TODO: แปลงกลับเป็น Event object
