from datetime import datetime, timezone

from meetup_gmail_calendar_sync.ics_parser import dedupe_latest, parse_ics_bytes


def test_parse_and_dedupe_latest_sequence():
    message_ts = datetime(2026, 2, 11, 12, 0, tzinfo=timezone.utc)

    ics_v1 = b"\n".join(
        [
            b"BEGIN:VCALENDAR",
            b"VERSION:2.0",
            b"BEGIN:VEVENT",
            b"UID:abc-123",
            b"SEQUENCE:1",
            b"DTSTAMP:20260210T120000Z",
            b"DTSTART:20260220T170000Z",
            b"DTEND:20260220T190000Z",
            b"SUMMARY:Meetup One",
            b"DESCRIPTION:https://www.meetup.com/x/events/1",
            b"END:VEVENT",
            b"END:VCALENDAR",
            b"",
        ]
    )

    ics_v2 = b"\n".join(
        [
            b"BEGIN:VCALENDAR",
            b"VERSION:2.0",
            b"BEGIN:VEVENT",
            b"UID:abc-123",
            b"SEQUENCE:2",
            b"DTSTAMP:20260211T120000Z",
            b"DTSTART:20260220T170000Z",
            b"DTEND:20260220T200000Z",
            b"SUMMARY:Meetup One Updated",
            b"DESCRIPTION:https://www.meetup.com/x/events/1",
            b"END:VEVENT",
            b"END:VCALENDAR",
            b"",
        ]
    )

    events = parse_ics_bytes(ics_v1, message_ts) + parse_ics_bytes(ics_v2, message_ts)
    deduped = dedupe_latest(events)

    assert len(deduped) == 1
    assert deduped["abc-123"].sequence == 2
    assert deduped["abc-123"].summary == "Meetup One Updated"
