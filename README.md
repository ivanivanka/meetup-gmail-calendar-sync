# Meetup Gmail Calendar Sync

Sync Meetup `.ics` invite emails from Gmail into a Google Calendar.

This tool avoids Meetup API keys and uses the invites that Meetup already sends to your inbox.

## Features

- Reads Meetup invite emails from Gmail (query configurable).
- Parses `.ics` attachments and deduplicates updates by `UID` + `SEQUENCE`.
- Creates/updates/deletes Google Calendar events idempotently.
- Works with recurring scheduled runs (daily cron/launchd).

## Install

```bash
git clone https://github.com/ivanivanka/meetup-gmail-calendar-sync.git
cd meetup-gmail-calendar-sync
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Google setup (one time)

1. Open Google Cloud Console and create/select a project.
2. Enable APIs:
- Gmail API
- Google Calendar API
3. Create OAuth client credentials for a Desktop app.
4. Download the JSON and save it as `credentials.json`.

## Authenticate (one time)

```bash
meetup-gcal-sync auth --credentials ./credentials.json --token ./token.json
```

If your environment is headless:

```bash
meetup-gcal-sync auth --credentials ./credentials.json --token ./token.json --console
```

Tip:
- If you skip `--credentials` and `--token`, defaults are used:
  - `~/.config/meetup-gcal-sync/credentials.json`
  - `~/.config/meetup-gcal-sync/token.json`

## Run sync

Dry run first:

```bash
meetup-gcal-sync sync \
  --credentials ./credentials.json \
  --token ./token.json \
  --calendar-name "Meetup" \
  --dry-run --verbose
```

Real sync:

```bash
meetup-gcal-sync sync \
  --credentials ./credentials.json \
  --token ./token.json \
  --calendar-name "Meetup"
```

## Useful options

- `--query`: Gmail query to find Meetup invites.
- `--max-messages`: Limit mailbox scan cost (default `500`).
- `--lookback-days`: Ignore old events that ended long ago (default `2`).

Default query:

```text
from:meetup filename:ics newer_than:730d
```

## Daily scheduling

### macOS launchd

```bash
bash scripts/install_launchd.sh \
  --credentials /abs/path/credentials.json \
  --token /abs/path/token.json \
  --hour 7 --minute 0
```

### Linux cron

```bash
0 7 * * * /abs/path/to/.venv/bin/meetup-gcal-sync sync --credentials /abs/path/credentials.json --token /abs/path/token.json --calendar-name "Meetup" >> /abs/path/meetup-sync.log 2>&1
```

## Security

- Never commit `credentials.json` or `token.json`.
- Keep OAuth files outside version control and use local paths.
- Token files are permission-hardened to owner-only (`600`) on POSIX systems.
- CI and pre-commit run credential leak scanning (`gitleaks`).

## License

MIT
