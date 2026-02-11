"""Google OAuth helpers."""

from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import yaml
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from .config import GMAIL_MODIFY_SCOPE, GMAIL_READ_SCOPE


def parse_token_file(token_path: Path) -> dict[str, Any]:
    raw = token_path.read_text(encoding="utf-8").strip()
    if not raw:
        raise RuntimeError(f"Token file is empty: {token_path}")

    if raw.startswith("{"):
        data = json.loads(raw)
    else:
        data = yaml.safe_load(raw)
        if isinstance(data, dict) and isinstance(data.get("default"), str):
            data = json.loads(data["default"])

    if not isinstance(data, dict):
        raise RuntimeError(f"Unsupported token format: {token_path}")

    return data


def normalize_scopes(raw_scopes: Any) -> list[str]:
    if isinstance(raw_scopes, str):
        return [scope for scope in raw_scopes.split() if scope]
    if isinstance(raw_scopes, list):
        return [str(scope) for scope in raw_scopes if str(scope).strip()]
    return []


def _scope_satisfied(required_scope: str, token_scopes: list[str]) -> bool:
    if required_scope in token_scopes:
        return True
    # Gmail modify includes read access.
    if required_scope == GMAIL_READ_SCOPE and GMAIL_MODIFY_SCOPE in token_scopes:
        return True
    return False


def _authorized_user_info(credentials_path: Path, token_data: dict[str, Any]) -> dict[str, Any]:
    credentials_doc = json.loads(credentials_path.read_text(encoding="utf-8"))
    installed = credentials_doc.get("installed", credentials_doc.get("web"))
    if not installed:
        raise RuntimeError("Client credentials JSON missing 'installed' or 'web'.")

    token_scopes = normalize_scopes(token_data.get("scope") or token_data.get("scopes"))
    return {
        "token": token_data.get("token") or token_data.get("access_token"),
        "refresh_token": token_data.get("refresh_token"),
        "token_uri": token_data.get("token_uri") or "https://oauth2.googleapis.com/token",
        "client_id": token_data.get("client_id") or installed.get("client_id"),
        "client_secret": token_data.get("client_secret") or installed.get("client_secret"),
        "scopes": token_scopes,
    }


def build_credentials(
    credentials_path: Path,
    token_path: Path,
    *,
    required_scopes: Iterable[str],
    auto_refresh: bool = True,
) -> Credentials:
    if not credentials_path.exists():
        raise RuntimeError(f"Credentials file not found: {credentials_path}")
    if not token_path.exists():
        raise RuntimeError(
            f"Token file not found: {token_path}. Run `meetup-gcal-sync auth` first."
        )

    token_data = parse_token_file(token_path)
    authorized_user = _authorized_user_info(credentials_path, token_data)

    scopes = normalize_scopes(authorized_user.get("scopes"))
    required = list(required_scopes)
    missing = [scope for scope in required if not _scope_satisfied(scope, scopes)]
    if missing:
        raise RuntimeError(
            "Token is missing required scopes. "
            f"Missing: {', '.join(missing)}. Run `meetup-gcal-sync auth` again."
        )

    creds = Credentials.from_authorized_user_info(authorized_user, scopes=scopes)

    if auto_refresh and not creds.valid and creds.refresh_token:
        creds.refresh(Request())

    if not creds.valid:
        raise RuntimeError("Google credentials are invalid. Run `meetup-gcal-sync auth` again.")

    return creds


def run_oauth_and_store_token(
    credentials_path: Path,
    token_path: Path,
    *,
    scopes: list[str],
    use_console: bool = False,
    port: int = 0,
) -> Path:
    if not credentials_path.exists():
        raise RuntimeError(f"Credentials file not found: {credentials_path}")

    flow = InstalledAppFlow.from_client_secrets_file(str(credentials_path), scopes=scopes)
    if use_console:
        creds = flow.run_console()
    else:
        creds = flow.run_local_server(port=port)

    token_path.parent.mkdir(parents=True, exist_ok=True)
    token_path.write_text(creds.to_json(), encoding="utf-8")
    return token_path
