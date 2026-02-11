"""CLI for meetup-gmail-calendar-sync."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from googleapiclient.errors import HttpError

from .auth import run_oauth_and_store_token
from .config import (
    CALENDAR_NAME_DEFAULT,
    DEFAULT_CREDENTIALS_PATH,
    DEFAULT_TOKEN_PATH,
    GMAIL_QUERY_DEFAULT,
    REQUIRED_SCOPES,
)
from .sync import run_sync


def _path(value: str) -> Path:
    return Path(value).expanduser().resolve()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="meetup-gcal-sync",
        description="Sync Meetup ICS invites from Gmail into Google Calendar.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    auth_parser = subparsers.add_parser("auth", help="Run Google OAuth and store token.")
    auth_parser.add_argument(
        "--credentials",
        type=_path,
        default=DEFAULT_CREDENTIALS_PATH,
        help=f"Path to OAuth client secret JSON (default: {DEFAULT_CREDENTIALS_PATH})",
    )
    auth_parser.add_argument(
        "--token",
        type=_path,
        default=DEFAULT_TOKEN_PATH,
        help=f"Path to token JSON output (default: {DEFAULT_TOKEN_PATH})",
    )
    auth_parser.add_argument(
        "--console",
        action="store_true",
        help="Use console auth flow instead of opening a local web server.",
    )
    auth_parser.add_argument(
        "--port",
        type=int,
        default=0,
        help="Port for local OAuth callback server (default: random free port).",
    )

    sync_parser = subparsers.add_parser("sync", help="Sync Meetup events into Google Calendar.")
    sync_parser.add_argument(
        "--credentials",
        type=_path,
        default=DEFAULT_CREDENTIALS_PATH,
        help=f"Path to OAuth client secret JSON (default: {DEFAULT_CREDENTIALS_PATH})",
    )
    sync_parser.add_argument(
        "--token",
        type=_path,
        default=DEFAULT_TOKEN_PATH,
        help=f"Path to token JSON (default: {DEFAULT_TOKEN_PATH})",
    )
    sync_parser.add_argument(
        "--calendar-name",
        default=CALENDAR_NAME_DEFAULT,
        help=f"Destination calendar name (default: {CALENDAR_NAME_DEFAULT})",
    )
    sync_parser.add_argument(
        "--query",
        default=GMAIL_QUERY_DEFAULT,
        help=f"Gmail query for Meetup ICS emails (default: {GMAIL_QUERY_DEFAULT})",
    )
    sync_parser.add_argument(
        "--max-messages",
        type=int,
        default=500,
        help="Maximum matching Gmail messages to scan (default: 500)",
    )
    sync_parser.add_argument(
        "--lookback-days",
        type=int,
        default=2,
        help="Ignore events that ended before this lookback window (default: 2)",
    )
    sync_parser.add_argument("--dry-run", action="store_true", help="Do not write to calendar.")
    sync_parser.add_argument("--verbose", action="store_true", help="Verbose output.")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "auth":
            token_path = run_oauth_and_store_token(
                credentials_path=args.credentials,
                token_path=args.token,
                scopes=REQUIRED_SCOPES,
                use_console=args.console,
                port=args.port,
            )
            print(f"token saved: {token_path}")
            return 0

        if args.command == "sync":
            calendar_id, stats = run_sync(
                credentials_path=args.credentials,
                token_path=args.token,
                calendar_name=args.calendar_name,
                query=args.query,
                max_messages=args.max_messages,
                lookback_days=args.lookback_days,
                dry_run=args.dry_run,
                verbose=args.verbose,
            )
            print(f"calendar_id={calendar_id}")
            print(
                "sync complete "
                f"parsed={stats.parsed} deduped={stats.deduped} processed={stats.processed} "
                f"created={stats.created} updated={stats.updated} "
                f"deleted={stats.deleted} skipped={stats.skipped} dry_run={stats.dry_run}"
            )
            return 0

        parser.error(f"Unknown command: {args.command}")
        return 2
    except HttpError as exc:
        print(f"google api error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
