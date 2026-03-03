# CLAUDE.md — meetup-gmail-calendar-sync

Syncs Meetup .ics invite emails from Gmail into Google Calendar.

---

## What This Repo Is

This tool reads Meetup invite emails from Gmail, parses `.ics` attachments, deduplicates by UID + SEQUENCE, and creates/updates/deletes Google Calendar events idempotently. It avoids the Meetup API entirely, relying on the invites Meetup already sends to your inbox. Designed for recurring scheduled runs via cron or launchd.

## What This Repo Is NOT

- NOT a general calendar sync tool (Meetup-specific only)
- NOT a Meetup API client (uses Gmail as the data source)

---

## Shared Contracts

| Contract | Path | Covers |
|----------|------|--------|
| Architecture | `~/.codex/SYSTEM.md` | 4 layers, entity model |
| Operations | `~/.codex/AGENTS.md` | Commits, PRs, labels |

---

## Rules

- **Commits:** `<type>(meetup-gmail-calendar-sync): <summary>` per `~/.codex/AGENTS.md`.
- **No secrets.** No API keys, tokens, or credentials in code or commits. OAuth tokens stored externally.
