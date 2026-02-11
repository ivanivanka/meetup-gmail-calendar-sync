.PHONY: setup lint test

setup:
	python3 -m venv .venv
	.venv/bin/pip install -U pip
	.venv/bin/pip install -e .[dev]

lint:
	.venv/bin/ruff check .
	.venv/bin/ruff format --check .

test:
	.venv/bin/pytest -q
