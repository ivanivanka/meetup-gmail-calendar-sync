"""Configuration defaults for meetup-gmail-calendar-sync."""

from __future__ import annotations

import os
from pathlib import Path

APP_NAME = "meetup-gcal-sync"
GMAIL_QUERY_DEFAULT = "from:meetup filename:ics newer_than:730d"
CALENDAR_NAME_DEFAULT = "Meetup"

CALENDAR_SCOPE = "https://www.googleapis.com/auth/calendar"
GMAIL_READ_SCOPE = "https://www.googleapis.com/auth/gmail.readonly"
GMAIL_MODIFY_SCOPE = "https://www.googleapis.com/auth/gmail.modify"
REQUIRED_SCOPES = [CALENDAR_SCOPE, GMAIL_READ_SCOPE]


def _default_config_dir() -> Path:
    xdg = os.getenv("XDG_CONFIG_HOME")
    if xdg:
        return Path(xdg) / APP_NAME
    return Path.home() / ".config" / APP_NAME


DEFAULT_CONFIG_DIR = _default_config_dir()
DEFAULT_CREDENTIALS_PATH = Path(
    os.getenv("MEETUP_GCAL_CREDENTIALS", str(DEFAULT_CONFIG_DIR / "credentials.json"))
)
DEFAULT_TOKEN_PATH = Path(os.getenv("MEETUP_GCAL_TOKEN", str(DEFAULT_CONFIG_DIR / "token.json")))
