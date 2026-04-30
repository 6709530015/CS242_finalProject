from enum import Enum
from datetime import datetime

class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4

class Status(Enum):
    UPCOMING = 1
    TODAY = 2
    OVERDUE = 3

class Event:
    def __init__(self, id, title, date, subject, description, priority=Priority.MEDIUM, calendar_id=None):
        self._id = id
        self._title = title
        self._date = date
        self._subject = subject
        self._description = description
        self._priority = priority
        self._status = Status.UPCOMING
        self._calendar_id = calendar_id

    def get_days_until(self):
        return (self._date - datetime.now()).days

    def set_calendar_id(self, calendar_id):
        self._calendar_id = calendar_id
