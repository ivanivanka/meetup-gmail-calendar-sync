# Security Policy

## Supported versions

This project is currently in active development on `main`.

## Reporting a vulnerability

Please open a private GitHub security advisory for this repository.

## Secret handling rules

- Never commit `credentials.json`, `token.json`, or `.env` files.
- Use local files outside the repo when possible.
- Rotate compromised OAuth client secrets and refresh tokens immediately.

## Built-in protections

- `.gitignore` blocks common credential/token filenames.
- CI secret scanning runs on every push and pull request.
- Pre-commit includes checks to prevent accidental secret and private key commits.
