# PitchFrame

PitchFrame is a full-stack data science platform for exploring MLB data. It pipelines historical and live stats, applies statistical analysis and ML models like win probability and performance forecasting, and displays results through an interactive dashboard — built as a portfolio project to develop practical, production-style skills across data engineering, database design, and web development.

## Tech stack

- **Language**: Python
- **Database**: PostgreSQL
- **ORM / migrations**: SQLAlchemy, Alembic
- **Infrastructure**: Docker, Docker Compose
- **Data source**: MLB Stats API (REST)
- **Config/secrets**: `python-dotenv`, `.env`-based (nothing sensitive committed)

## Status

| Layer | Status |
|---|---|
| Data collection | Done — MLB Stats API client for schedules, boxscores, venues, and full play-by-play |
| Database schema | Done — 12-table Postgres schema, fully migrated |
| Loading pipeline | Done — full 2025 season loaded end-to-end into Postgres |
| Web backend / frontend | Not started |
| ML models | Not started |

A full 2025 MLB season (regular + postseason, ~2,500 games) is loaded end-to-end into a normalized Postgres schema — from official boxscore lines down to individual pitch physics (velocity, spin, release point, break) — via composite keys and foreign-key constraints instead of denormalized JSON blobs. Six materialized views (season, postseason, and career batting/pitching stats) sit on top of the raw data for fast querying. Every schema change is a version-controlled Alembic migration, and Postgres runs in Docker Compose for a reproducible local setup.

## Project structure

```
src/
  data_collection/   # fetch-only clients for external data sources (MLB Stats API, Statcast)
  db/                # SQLAlchemy models and engine/session setup
    models/
      reference.py   # Venue, Team, Player
      games.py       # Game, BattingBoxscore, PitchingBoxscore
      playbyplay.py  # AtBat, Event, Pitch, BattedBall, BaserunningEvent, BaserunningEventCredit
  pipeline/           # loads raw JSON into the database
    load_reference.py    # venues, teams, players
    load_games.py         # games, boxscores
    load_playbyplay.py     # at-bats, events, pitches, batted balls, baserunning
  models/             # (planned) ML training/eval/inference
  utils/              # shared config/logging
alembic/               # versioned schema migrations
web/                   # (planned) frontend + backend
```
