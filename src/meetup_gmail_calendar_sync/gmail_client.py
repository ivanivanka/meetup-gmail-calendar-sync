"""Gmail helpers for extracting Meetup ICS payloads."""

from __future__ import annotations

import base64
from collections.abc import Iterator
from datetime import datetime, timezone
from typing import Any


def decode_base64url(value: str) -> bytes:
    padding = "=" * ((4 - (len(value) % 4)) % 4)
    return base64.urlsafe_b64decode(value + padding)


def iter_payload_parts(payload: dict[str, Any]) -> Iterator[dict[str, Any]]:
    yield payload
    for part in payload.get("parts", []) or []:
        yield from iter_payload_parts(part)


def part_contains_calendar(part: dict[str, Any]) -> bool:
    mime_type = (part.get("mimeType") or "").lower()
    filename = (part.get("filename") or "").lower()
    return mime_type == "text/calendar" or filename.endswith(".ics")


def parse_message_ts(message: dict[str, Any]) -> datetime:
    internal_date_ms = int(message.get("internalDate", "0") or "0")
    if internal_date_ms <= 0:
        return datetime.now(timezone.utc)
    return datetime.fromtimestamp(internal_date_ms / 1000.0, tz=timezone.utc)


def load_ics_payloads(gmail_service: Any, message_id: str, payload: dict[str, Any]) -> list[bytes]:
    calendars: list[bytes] = []

    for part in iter_payload_parts(payload):
        if not part_contains_calendar(part):
            continue

        body = part.get("body", {}) or {}
        data = body.get("data")
        attachment_id = body.get("attachmentId")

        if data:
            calendars.append(decode_base64url(data))
            continue

        if attachment_id:
            attachment = (
                gmail_service.users()
                .messages()
                .attachments()
                .get(userId="me", messageId=message_id, id=attachment_id)
                .execute()
            )
            attachment_data = attachment.get("data")
            if attachment_data:
                calendars.append(decode_base64url(attachment_data))

    return calendars


def iter_messages(gmail_service: Any, query: str, max_messages: int) -> Iterator[dict[str, Any]]:
    seen = 0
    page_token = None

    while seen < max_messages:
        response = (
            gmail_service.users()
            .messages()
            .list(
                userId="me",
                q=query,
                maxResults=min(100, max_messages - seen),
                pageToken=page_token,
            )
            .execute()
        )

        messages = response.get("messages", [])
        if not messages:
            return

        for message_ref in messages:
            yield (
                gmail_service.users()
                .messages()
                .get(userId="me", id=message_ref["id"], format="full")
                .execute()
            )
            seen += 1
            if seen >= max_messages:
                return

        page_token = response.get("nextPageToken")
        if not page_token:
            return
