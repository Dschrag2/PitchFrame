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
| Data collection | Done — MLB Stats API client for schedules, boxscores, and full play-by-play |
| Database schema | Done — 12-table Postgres schema, fully migrated |
| Loading pipeline | Not started — parses raw JSON into the database |
| Web backend / frontend | Not started |
| ML models | Not started |

A full 2025 MLB season (regular + postseason, ~2,500 games) has been pulled to `data/raw/` and a normalized Postgres schema exists to hold it — modeling everything from official boxscore lines down to individual pitch physics (velocity, spin, release point, break) via composite keys and foreign-key constraints instead of denormalized JSON blobs. Every schema change is a version-controlled Alembic migration, and Postgres runs in Docker Compose for a reproducible local setup. The loading pipeline connecting the raw data to the schema is next.

## Project structure

```
src/
  data_collection/   # fetch-only clients for external data sources (MLB Stats API, Statcast)
  db/                # SQLAlchemy models and engine/session setup
    models/
      reference.py   # Venue, Team, Player
      games.py       # Game, BattingBoxscore, PitchingBoxscore
      playbyplay.py  # AtBat, Event, Pitch, BattedBall, BaserunningEvent, BaserunningEventCredit
  pipeline/           # (planned) cleans/joins raw data and loads it into the database
  models/             # (planned) ML training/eval/inference
  utils/              # shared config/logging
alembic/               # versioned schema migrations
web/                   # (planned) frontend + backend
```
