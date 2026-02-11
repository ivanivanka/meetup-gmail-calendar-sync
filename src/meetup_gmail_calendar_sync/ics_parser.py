"""ICS parsing and meetup event modeling."""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from typing import Any

from icalendar import Calendar

URL_PATTERN = re.compile(r"https?://\\S+")


@dataclass(frozen=True)
class MeetupEvent:
    uid: str
    sequence: int
    dtstamp: datetime
    message_ts: datetime
    status: str
    summary: str
    description: str
    location: str
    start: date | datetime
    end: date | datetime
    meetup_url: str


def _to_datetime_utc(value: Any, fallback: datetime) -> datetime:
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)
    return fallback


def _normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def parse_ics_bytes(ics_bytes: bytes, message_ts: datetime) -> list[MeetupEvent]:
    calendar = Calendar.from_ical(ics_bytes)
    events: list[MeetupEvent] = []

    for component in calendar.walk("VEVENT"):
        uid = _normalize_text(component.get("uid"))
        if not uid:
            continue

        status = _normalize_text(component.get("status") or "CONFIRMED").upper()

        raw_sequence = component.get("sequence")
        try:
            sequence = int(raw_sequence) if raw_sequence is not None else 0
        except Exception:
            sequence = 0

        dtstamp_raw = component.decoded("dtstamp") if component.get("dtstamp") else message_ts
        dtstamp = _to_datetime_utc(dtstamp_raw, message_ts)

        start = component.decoded("dtstart")
        if component.get("dtend"):
            end = component.decoded("dtend")
        elif isinstance(start, datetime):
            end = start + timedelta(hours=2)
        else:
            end = start + timedelta(days=1)

        summary = _normalize_text(component.get("summary") or "Meetup event")
        description = _normalize_text(component.get("description"))
        location = _normalize_text(component.get("location"))
        meetup_url_match = URL_PATTERN.search(description)
        meetup_url = meetup_url_match.group(0) if meetup_url_match else ""

        events.append(
            MeetupEvent(
                uid=uid,
                sequence=sequence,
                dtstamp=dtstamp,
                message_ts=message_ts,
                status=status,
                summary=summary,
                description=description,
                location=location,
                start=start,
                end=end,
                meetup_url=meetup_url,
            )
        )

    return events


def _rank(event: MeetupEvent) -> tuple[int, datetime, datetime]:
    return (event.sequence, event.dtstamp, event.message_ts)


def dedupe_latest(events: Iterable[MeetupEvent]) -> dict[str, MeetupEvent]:
    latest_by_uid: dict[str, MeetupEvent] = {}
    for event in events:
        current = latest_by_uid.get(event.uid)
        if current is None or _rank(event) > _rank(current):
            latest_by_uid[event.uid] = event
    return latest_by_uid
