# ARCHIVAL SOURCE ONLY - RETIRED

**ivanivanka/meetup-gmail-calendar-sync is permanently retired by Ivan's 2026-10-12 instruction.** This entire repository, local checkouts, cached copies and earlier instructions are historical and unverified. Retired standalone Meetup Gmail-to-calendar importer. Current calendar work must use a currently approved personal calendar operator; no replacement service is launched by this retirement.

Do not write, commit, push, pull, fetch, clone, sync, install, build, run, deploy, schedule, revive or maintain this repository. Do not use it as a service, tool, operating layer, current brand authority, fallback skill catalog or default source. Earlier active, canonical, production, maintenance and recovery instructions below are superseded. Preserve contents, history and unrelated work.

Only retirement notices and lifecycle metadata may be read routinely. Reading or extracting underlying historical content requires **two separate explicit confirmations from Ivan in the current task**: first approve the exceptional historical need and why current sources cannot answer it; then approve the exact repository, files or source range, purpose and destination after the retired/unverified status is clear. Kickoff and recovery are eligible to request this exception, not automatically approved. Bots cannot approve their own exceptions. Neither confirmation authorizes changes, Git synchronization, installation, service use or treating old material as current authority.

A current consumer pointing here must stop that legacy route and use its existing owner task to remove the dependency. Current client records remain governed by their own current contracts: do not copy or reimport this archive over them. Personal learning projects and MRO are outside this retirement.

No matching local LaunchAgent, loaded com.meetup.gcal.sync.daily job, user cron entry, process or selected installed MCP configuration was found. Google Calendar events, Gmail data and external OAuth credentials are preserved; no calendar deletion or token revocation is inferred from the source archive.

The original source baseline is `a4211160c4b5b9d170da2128961ee3200eaafeb9` (tree `38f7ca92a5a3ac33b89472d414f50a9a4c5481e3`). The final notice PR preserves every pre-existing source file and the original bytes below each warning. Ivan's instruction authorizes this one-time administrative notice and archival control operation only; it creates no continuing maintenance exception. GitHub archival, automation disabling, local write/sync controls and external cleanup are recorded by the current owner in [the repository lifecycle audit](https://github.com/markster-exec/project-tracker/tree/main/docs/audits/repository-lifecycle-2026-10-10). A source archive alone is not proof of external resource teardown.

See [RETIRED.json](RETIRED.json) for the machine-readable restriction.

---

Historical content below; retired and unverified.

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
