from database import create_tables, get_all_events, delete_event

create_tables()

events = get_all_events()

print("All events from database:")
for event in events:
    print(event)