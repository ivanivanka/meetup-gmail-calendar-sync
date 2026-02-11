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
