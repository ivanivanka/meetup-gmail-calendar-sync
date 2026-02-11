"""Google Calendar sync operations."""

from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone
from typing import Any

from .ics_parser import MeetupEvent


def ensure_calendar(calendar_service: Any, calendar_name: str) -> str:
    page_token = None
    while True:
        result = (
            calendar_service.calendarList()
            .list(pageToken=page_token, minAccessRole="owner", showHidden=False)
            .execute()
        )
        for item in result.get("items", []):
            if item.get("summary") == calendar_name:
                return item["id"]
        page_token = result.get("nextPageToken")
        if not page_token:
            break

    primary = calendar_service.calendars().get(calendarId="primary").execute()
    created = (
        calendar_service.calendars()
        .insert(
            body={
                "summary": calendar_name,
                "description": "Auto-synced from Meetup Gmail invites",
                "timeZone": primary.get("timeZone", "UTC"),
            }
        )
        .execute()
    )
    return created["id"]


def event_not_too_old(event: MeetupEvent, lookback_days: int) -> bool:
    cutoff = datetime.now(timezone.utc) - timedelta(days=lookback_days)
    if isinstance(event.end, datetime):
        end_dt = event.end if event.end.tzinfo else event.end.replace(tzinfo=timezone.utc)
        return end_dt.astimezone(timezone.utc) >= cutoff
    end_dt = datetime.combine(event.end, time.min, tzinfo=timezone.utc)
    return end_dt >= cutoff


def event_start_sort_key(value: date | datetime) -> datetime:
    if isinstance(value, datetime):
        dt = value if value.tzinfo else value.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    return datetime.combine(value, time.min, tzinfo=timezone.utc)


def to_google_event_time(value: date | datetime) -> dict[str, str]:
    if isinstance(value, datetime):
        dt = value if value.tzinfo else value.replace(tzinfo=timezone.utc)
        return {"dateTime": dt.isoformat()}
    return {"date": value.isoformat()}


def build_calendar_body(event: MeetupEvent) -> dict[str, Any]:
    description = event.description or ""
    if "Auto-synced from Meetup Gmail invites" not in description:
        description = f"{description}\n\nAuto-synced from Meetup Gmail invites".strip()

    body: dict[str, Any] = {
        "summary": event.summary,
        "description": description,
        "location": event.location,
        "start": to_google_event_time(event.start),
        "end": to_google_event_time(event.end),
        "extendedProperties": {
            "private": {
                "sync_source": "meetup-gmail-sync",
                "meetup_uid": event.uid,
            }
        },
    }
    if event.meetup_url:
        body["source"] = {"title": "Meetup", "url": event.meetup_url}
    return body


def find_existing_event_by_uid(
    calendar_service: Any, calendar_id: str, uid: str
) -> dict[str, Any] | None:
    result = (
        calendar_service.events()
        .list(calendarId=calendar_id, iCalUID=uid, showDeleted=True, maxResults=5)
        .execute()
    )
    items = result.get("items", [])
    return items[0] if items else None
