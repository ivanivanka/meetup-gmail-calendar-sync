#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LABEL="com.meetup.gcal.sync.daily"
HOUR="7"
MINUTE="0"
CALENDAR_NAME="Meetup"
CREDENTIALS=""
TOKEN=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --credentials)
      CREDENTIALS="$2"
      shift 2
      ;;
    --token)
      TOKEN="$2"
      shift 2
      ;;
    --calendar-name)
      CALENDAR_NAME="$2"
      shift 2
      ;;
    --hour)
      HOUR="$2"
      shift 2
      ;;
    --minute)
      MINUTE="$2"
      shift 2
      ;;
    *)
      echo "Unknown arg: $1" >&2
      exit 1
      ;;
  esac
done

if [[ -z "$CREDENTIALS" || -z "$TOKEN" ]]; then
  echo "Usage: $0 --credentials /abs/path/credentials.json --token /abs/path/token.json [--calendar-name Meetup] [--hour 7] [--minute 0]" >&2
  exit 1
fi

if [[ ! -f "$ROOT_DIR/.venv/bin/meetup-gcal-sync" ]]; then
  echo "Missing executable: $ROOT_DIR/.venv/bin/meetup-gcal-sync" >&2
  echo "Run: python3 -m venv .venv && source .venv/bin/activate && pip install -e ." >&2
  exit 1
fi

LAUNCH_AGENTS="$HOME/Library/LaunchAgents"
PLIST_PATH="$LAUNCH_AGENTS/${LABEL}.plist"
LOG_DIR="$ROOT_DIR/logs"
mkdir -p "$LAUNCH_AGENTS" "$LOG_DIR"

cat > "$PLIST_PATH" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>${LABEL}</string>

  <key>ProgramArguments</key>
  <array>
    <string>${ROOT_DIR}/.venv/bin/meetup-gcal-sync</string>
    <string>sync</string>
    <string>--credentials</string>
    <string>${CREDENTIALS}</string>
    <string>--token</string>
    <string>${TOKEN}</string>
    <string>--calendar-name</string>
    <string>${CALENDAR_NAME}</string>
  </array>

  <key>WorkingDirectory</key>
  <string>${ROOT_DIR}</string>

  <key>RunAtLoad</key>
  <true/>

  <key>StartCalendarInterval</key>
  <dict>
    <key>Hour</key>
    <integer>${HOUR}</integer>
    <key>Minute</key>
    <integer>${MINUTE}</integer>
  </dict>

  <key>StandardOutPath</key>
  <string>${LOG_DIR}/meetup-sync.out.log</string>

  <key>StandardErrorPath</key>
  <string>${LOG_DIR}/meetup-sync.err.log</string>
</dict>
</plist>
PLIST

launchctl bootout "gui/$(id -u)/${LABEL}" >/dev/null 2>&1 || true
launchctl bootstrap "gui/$(id -u)" "$PLIST_PATH"
launchctl kickstart -k "gui/$(id -u)/${LABEL}"

echo "Installed launchd job: ${LABEL}"
echo "Plist: ${PLIST_PATH}"
