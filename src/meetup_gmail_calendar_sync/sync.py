"""End-to-end sync orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from googleapiclient.discovery import build

from .auth import build_credentials
from .calendar_client import (
    build_calendar_body,
    ensure_calendar,
    event_not_too_old,
    event_start_sort_key,
    find_existing_event_by_uid,
)
from .config import CALENDAR_SCOPE, GMAIL_READ_SCOPE
from .gmail_client import iter_messages, load_ics_payloads, parse_message_ts
from .ics_parser import dedupe_latest, parse_ics_bytes


@dataclass
class SyncStats:
    parsed: int = 0
    deduped: int = 0
    processed: int = 0
    created: int = 0
    updated: int = 0
    deleted: int = 0
    skipped: int = 0
    dry_run: bool = False


def _sync_scopes() -> list[str]:
    return [CALENDAR_SCOPE, GMAIL_READ_SCOPE]


def collect_events(
    gmail_service: Any,
    *,
    query: str,
    max_messages: int,
    verbose: bool,
):
    events = []

    for message in iter_messages(gmail_service, query=query, max_messages=max_messages):
        message_id = message["id"]
        message_ts = parse_message_ts(message)
        payload = message.get("payload", {})
        ics_payloads = load_ics_payloads(gmail_service, message_id=message_id, payload=payload)

        if verbose:
            print(f"message {message_id}: found {len(ics_payloads)} ICS attachment(s)")

        for ics_bytes in ics_payloads:
            try:
                events.extend(parse_ics_bytes(ics_bytes, message_ts=message_ts))
            except Exception as exc:
                print(f"warning: failed to parse ICS for message {message_id}: {exc}")

    return events


def run_sync(
    *,
    credentials_path: Path,
    token_path: Path,
    calendar_name: str,
    query: str,
    max_messages: int,
    lookback_days: int,
    dry_run: bool,
    verbose: bool,
) -> tuple[str, SyncStats]:
    creds = build_credentials(
        credentials_path=credentials_path,
        token_path=token_path,
        required_scopes=_sync_scopes(),
    )
    gmail_service = build("gmail", "v1", credentials=creds, cache_discovery=False)
    calendar_service = build("calendar", "v3", credentials=creds, cache_discovery=False)

    calendar_id = ensure_calendar(calendar_service, calendar_name=calendar_name)
    if verbose:
        print(f"using calendar: {calendar_id}")

    all_events = collect_events(
        gmail_service,
        query=query,
        max_messages=max_messages,
        verbose=verbose,
    )
    deduped = dedupe_latest(all_events)
    eligible = [event for event in deduped.values() if event_not_too_old(event, lookback_days)]
    eligible.sort(key=lambda event: event_start_sort_key(event.start))

    stats = SyncStats(
        parsed=len(all_events),
        deduped=len(deduped),
        processed=len(eligible),
        dry_run=dry_run,
    )

    for event in eligible:
        existing = find_existing_event_by_uid(calendar_service, calendar_id, event.uid)

        if event.status == "CANCELLED":
            if dry_run:
                if existing:
                    print(f"dry-run delete: {event.summary} ({event.uid})")
                    stats.deleted += 1
                else:
                    stats.skipped += 1
                continue

            if existing and existing.get("status") != "cancelled":
                calendar_service.events().delete(
                    calendarId=calendar_id,
                    eventId=existing["id"],
                    sendUpdates="none",
                ).execute()
                stats.deleted += 1
            else:
                stats.skipped += 1
            continue

        body = build_calendar_body(event)

        if dry_run:
            if existing:
                print(f"dry-run update: {event.summary} ({event.uid})")
                stats.updated += 1
            else:
                print(f"dry-run create: {event.summary} ({event.uid})")
                stats.created += 1
            continue

        if existing:
            calendar_service.events().patch(
                calendarId=calendar_id,
                eventId=existing["id"],
                body=body,
                sendUpdates="none",
            ).execute()
            stats.updated += 1
        else:
            import_body = dict(body)
            import_body["iCalUID"] = event.uid
            calendar_service.events().import_(calendarId=calendar_id, body=import_body).execute()
            stats.created += 1

    return calendar_id, stats
