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

# Repo Agent Guide

## Scope

This repository provides a reusable CLI to sync Meetup ICS invites from Gmail into Google Calendar.

## Development rules

- Keep secrets out of git. Never commit OAuth credentials/tokens.
- Prefer small, reversible changes.
- Add tests for behavior changes where practical.
- Keep CLI UX backward-compatible when possible.

## Commands

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
ruff check .
pytest -q
```
