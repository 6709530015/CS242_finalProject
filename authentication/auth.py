import os
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import pickle #for token
import datetime #for testing

SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/calendar.events"
]

#dynamic path to find token and secret
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREDENTIALS_DIR = os.path.join(BASE_DIR, "authentication", "credentials")

TOKEN_FILE = os.path.join(CREDENTIALS_DIR, "token.pickle")
CLIENT_SECRET_FILE = os.path.join(CREDENTIALS_DIR, "credentials.json")

#เรียก token
def get_service():
    creds = None
    
    #token exist
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as f:
            creds = pickle.load(f)

    #token unavailable
    if not creds or not creds.valid:
        #token expired
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                print("Token refreshed successfully")
            except Exception as e:
                print(f"Refresh failed: {e}")
                creds = None
        
        #token not exist
        if not creds or not creds.valid:
            print("Starting new OAuth flow...")
            #ไฟล์ secret ไม่อยู่
            if not os.path.exists(CLIENT_SECRET_FILE):
                raise FileNotFoundError(f"client_secret.json not found at {CLIENT_SECRET_FILE}")
            
            #open login
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0, access_type="offline", prompt="consent")
            print("New authorization completed!")

        # Save credentials
        os.makedirs(CREDENTIALS_DIR, exist_ok=True)
        with open(TOKEN_FILE, "wb") as f:
            pickle.dump(creds, f)
            print(f"Credentials saved to {TOKEN_FILE}")

    service = build("calendar", "v3", credentials=creds)
    return service

def add_event_to_google_calendar(service, title, date, description, subject):
    event_body = {
        "summary": title,
        "description": f"[{subject}] {description}",
        "start": {"date": date},  # "YYYY-MM-DD" format
        "end":   {"date": date},
    }
    created = service.events().insert(calendarId="primary", body=event_body).execute()
    return created.get("id") #calendar_id

def logout_google():
    """Removes the local token.pickle file to log the user out."""
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)
        print(f"Logged out: {TOKEN_FILE} removed.")
        return True
    else:
        print("No active session found.")
        return False