# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**pygameday** is a Python package that scrapes MLB GameDay data (games, players, at-bats, pitches, hits in play) from the MLB GameDay website, parses it, and inserts it into a relational database via SQLAlchemy.

## Commands

```bash
# Install project + dev dependencies (creates .venv automatically)
uv sync --group dev

# Run all tests
uv run python -m unittest discover tests/

# Run a single test file
uv run python -m unittest tests.test_GameDayClient

# Run a single test method
uv run python -m unittest tests.test_GameDayClient.TestGameDayClient.test_ingest

# Build distribution
make dist          # runs `uv build`

# Clean build artifacts
make clean
```

## Architecture

Data flows through four layers:

1. **`scrape.py`** — Fetches raw XML/JSON pages from `gd2.mlb.com`. Functions named `fetch_*` return raw page content. The `get_url()` helper handles HTTP with error logging.

2. **`parse.py`** — Parses raw pages (via `lxml.etree`) into SQLAlchemy model instances. Functions named `parse_*` return lists of model objects. `parse_game()` filters out non-Final games. `parse_inning_all()` builds nested AtBat→Pitch trees.

3. **`models.py`** — SQLAlchemy ORM models: `Game`, `AtBat`, `Pitch`, `Player`, `HitInPlay`. `db_connect()` creates the engine; `create_db_tables()` creates tables if missing.

4. **`client.py`** — `GameDayClient` orchestrates everything. Key design points:
   - Uses `ProcessPoolExecutor` for parallel game processing; each worker opens its own DB connection to avoid threading issues.
   - Maintains in-memory sets (`inserted_game_ids`, `inserted_player_ids`) to skip duplicates without repeated DB queries.
   - `process_game()` is the per-game worker: scrapes → parses → inserts a complete game in one transaction.
   - `process_date_range()` iterates dates and calls `process_date()` → `process_game()` in parallel.

**Public API:** `from pygameday import GameDayClient` — `GameDayClient` is the only export.

## Database

SQLAlchemy handles all DB access; pass any SQLAlchemy connection URI to `GameDayClient(database_uri)`. Tested dialects include SQLite, PostgreSQL, MySQL. Tables use `Sequence`-based primary keys and foreign keys for `Game → AtBat → Pitch` and `Game → HitInPlay`.

## Key Behaviors

- Spring training games are skipped by default (`ingest_spring_training=False`).
- Only games with status `'Final'` are processed.
- `IntegrityError` on duplicate insert is caught and silently skipped; other exceptions are logged but don't abort a date range.
- Logs write to `logs/pygameday.log` (rotating, 5 MB max, 5 backups) and to console.
