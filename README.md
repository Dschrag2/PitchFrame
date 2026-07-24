# PitchFrame

PitchFrame is a full-stack data science platform for exploring MLB data. It pipelines historical and live stats, applies statistical analysis and ML models like win probability and performance forecasting, and displays results through an interactive dashboard — built as a portfolio project to develop practical, production-style skills across data engineering, database design, and web development.

## Tech stack

- **Language**: Python, TypeScript
- **Database**: PostgreSQL
- **ORM / migrations**: SQLAlchemy, Alembic
- **Web backend**: FastAPI, Pydantic
- **Web frontend**: Next.js (App Router), React, Tailwind CSS
- **Infrastructure**: Docker, Docker Compose
- **Data source**: MLB Stats API (REST)
- **Config/secrets**: `python-dotenv`, `.env`-based (nothing sensitive committed)

## Status

| Layer | Status |
|---|---|
| Data collection | Done — MLB Stats API client for schedules, boxscores, venues, and full play-by-play |
| Database schema | Done — 12-table Postgres schema, fully migrated |
| Loading pipeline | Done — full 2025 season loaded end-to-end into Postgres |
| Web backend | In progress — FastAPI serving games, teams, players, boxscores, leaderboards, and BvP matchup endpoints |
| Web frontend | In progress — Next.js app with games, boxscore, leaderboard, and player pages, styled with real team colors |
| ML models | Not started |

A full 2025 MLB season (regular + postseason, ~2,500 games) is loaded end-to-end into a normalized Postgres schema — from official boxscore lines down to individual pitch physics (velocity, spin, release point, break) — via composite keys and foreign-key constraints instead of denormalized JSON blobs. Six materialized views (season, postseason, and career batting/pitching stats) sit on top of the raw data for fast querying. Every schema change is a version-controlled Alembic migration, and Postgres runs in Docker Compose for a reproducible local setup.

A FastAPI backend exposes that data — game lists and boxscores, team rosters, player search with career/season/postseason batting and pitching stats, batter-vs-pitcher matchups, and stat leaderboards — using Pydantic schemas kept separate from the SQLAlchemy models. A Next.js frontend (TypeScript, Tailwind) consumes it server-side, with a shared component library (`Card`, `StatTable`, `TeamBadge`) and a real MLB team-color lookup driving a consistent look across the games list, boxscore, leaderboard, and player pages. A header with live player search sits on every page.

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
web/
  backend/            # FastAPI app (reuses src/db directly, no duplicated models)
    routers/           # games, teams, players, matchups, leaderboards endpoints
    schemas/            # Pydantic response models
  frontend/           # Next.js app (App Router, TypeScript, Tailwind)
    src/app/            # pages: games list, boxscore, leaderboards, player detail
    src/components/       # shared UI: Card, StatTable, TeamBadge, Header
    src/lib/api.ts        # typed API client
    src/lib/team-colors.ts # MLB team id -> brand color lookup
```
