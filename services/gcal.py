"""Google Calendar API — list, create, update, delete events.

NOTE: Scope changed from calendar.readonly to calendar (full read/write).
If OAuth token was issued with readonly scope, user may need to re-authorize.
"""
import os
import json
import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

logger = logging.getLogger("gcal")
TZ = ZoneInfo("Europe/Berlin")


def _get_cal_service():
    creds_json = os.environ.get("GOOGLE_CREDENTIALS_JSON", "")
    creds_data = json.loads(creds_json)
    creds = Credentials(
        token=None,
        refresh_token=creds_data["refresh_token"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=creds_data["client_id"],
        client_secret=creds_data["client_secret"],
        scopes=["https://www.googleapis.com/auth/calendar"],
    )
    return build("calendar", "v3", credentials=creds)


async def get_events(day: str = "today") -> list:
    """Get calendar events for today or tomorrow."""
    service = _get_cal_service()
    now = datetime.now(TZ)

    if day == "tomorrow":
        start = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    end = start + timedelta(days=1)

    result = service.events().list(
        calendarId="primary",
        timeMin=start.isoformat(),
        timeMax=end.isoformat(),
        singleEvents=True,
        orderBy="startTime",
        timeZone="Europe/Berlin",
    ).execute()

    events = []
    for e in result.get("items", []):
        start_str = e["start"].get("dateTime", e["start"].get("date", ""))
        events.append({
            "id": e.get("id", ""),
            "title": e.get("summary", "No Title"),
            "start": start_str,
            "end": e["end"].get("dateTime", e["end"].get("date", "")),
            "location": e.get("location", ""),
            "attendees": len(e.get("attendees", [])),
        })
    return events


async def create_event(title: str, start_time: str, end_time: str,
                       description: str = "", location: str = "",
                       attendees: list = None) -> dict:
    """Create a calendar event.

    Args:
        title: Event title/summary
        start_time: ISO format datetime (e.g. '2026-03-16T14:00:00')
        end_time: ISO format datetime (e.g. '2026-03-16T15:00:00')
        description: Optional event description
        location: Optional location
        attendees: Optional list of email addresses
    """
    service = _get_cal_service()
    event_body = {
        "summary": title,
        "start": {"dateTime": start_time, "timeZone": "Europe/Berlin"},
        "end": {"dateTime": end_time, "timeZone": "Europe/Berlin"},
    }
    if description:
        event_body["description"] = description
    if location:
        event_body["location"] = location
    if attendees:
        event_body["attendees"] = [{"email": e} for e in attendees]

    created = service.events().insert(
        calendarId="primary", body=event_body, sendUpdates="all"
    ).execute()

    return {
        "id": created.get("id", ""),
        "title": created.get("summary", ""),
        "start": created["start"].get("dateTime", ""),
        "end": created["end"].get("dateTime", ""),
        "link": created.get("htmlLink", ""),
        "status": "created",
    }


async def update_event(event_id: str, title: str = None, start_time: str = None,
                       end_time: str = None, description: str = None,
                       location: str = None) -> dict:
    """Update an existing calendar event.

    Args:
        event_id: Google Calendar event ID
        title: New title (optional)
        start_time: New start time ISO format (optional)
        end_time: New end time ISO format (optional)
        description: New description (optional)
        location: New location (optional)
    """
    service = _get_cal_service()
    # First get current event
    existing = service.events().get(calendarId="primary", eventId=event_id).execute()

    if title:
        existing["summary"] = title
    if start_time:
        existing["start"] = {"dateTime": start_time, "timeZone": "Europe/Berlin"}
    if end_time:
        existing["end"] = {"dateTime": end_time, "timeZone": "Europe/Berlin"}
    if description is not None:
        existing["description"] = description
    if location is not None:
        existing["location"] = location

    updated = service.events().update(
        calendarId="primary", eventId=event_id, body=existing, sendUpdates="all"
    ).execute()

    return {
        "id": updated.get("id", ""),
        "title": updated.get("summary", ""),
        "start": updated["start"].get("dateTime", ""),
        "end": updated["end"].get("dateTime", ""),
        "link": updated.get("htmlLink", ""),
        "status": "updated",
    }


async def delete_event(event_id: str) -> dict:
    """Delete a calendar event.

    Args:
        event_id: Google Calendar event ID
    """
    service = _get_cal_service()
    service.events().delete(
        calendarId="primary", eventId=event_id, sendUpdates="all"
    ).execute()
    return {"event_id": event_id, "status": "deleted"}
