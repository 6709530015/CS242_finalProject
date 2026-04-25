from models.event_manager import EventManager

class ReminderSystem:
    def __init__(self, manager: EventManager):
        self._manager = manager

    def send_reminder(self):
        self._manager.update_all_status()
        for e in self._manager._events:
            if e._status == Status.TODAY:
                print(f"Reminder: {e._title} is due today!")

    def analyze_events(self):
        # ใช้ Pandas + Matplotlib ทำ visualization
        pass
