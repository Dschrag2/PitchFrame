"""
load_games.py

Loads the games table from schedule.json. Requires venues and teams to
already exist (load_reference.py must run first).
"""

import argparse
import json
from datetime import date, datetime
from pathlib import Path

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from db.base import SessionLocal
from db.models import Game


def _parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _dedupe_games(games: list[dict]) -> list[dict]:
    """Postponed/rescheduled games appear twice under the same gamePk (once as
    'Postponed', once as 'Final' on the makeup date). Keep the non-Postponed
    entry when there's a duplicate, regardless of which order they appear in."""
    by_pk: dict[int, dict] = {}
    for game in games:
        pk = game["gamePk"]
        existing = by_pk.get(pk)
        if existing is None or existing["status"]["detailedState"] == "Postponed":
            by_pk[pk] = game
    return list(by_pk.values())


def _game_row(game: dict) -> dict:
    home = game["teams"]["home"]
    away = game["teams"]["away"]
    rescheduled_from = game.get("rescheduledFrom")
    return {
        "id": game["gamePk"],
        "season": int(game["season"]),
        "game_type": game["gameType"],
        "game_date": _parse_datetime(game["gameDate"]),
        "official_date": date.fromisoformat(game["officialDate"]),
        "detailed_state": game["status"]["detailedState"],
        "day_night": game.get("dayNight"),
        "double_header": game["doubleHeader"],
        "game_number": game["gameNumber"],
        "venue_id": game["venue"]["id"],
        "home_team_id": home["team"]["id"],
        "away_team_id": away["team"]["id"],
        "home_score": home.get("score"),
        "away_score": away.get("score"),
        "is_tie": game.get("isTie", False),
        "scheduled_innings": game["scheduledInnings"],
        "series_game_number": game.get("seriesGameNumber"),
        "games_in_series": game.get("gamesInSeries"),
        "series_description": game.get("seriesDescription"),
        "rescheduled_from": _parse_datetime(rescheduled_from) if rescheduled_from else None,
    }


def load_games(session: Session, schedule_path: Path) -> int:
    games_data = _dedupe_games(json.loads(schedule_path.read_text()))
    rows = [_game_row(g) for g in games_data]

    stmt = pg_insert(Game).values(rows)
    update_cols = {c.name: getattr(stmt.excluded, c.name) for c in Game.__table__.columns if c.name != "id"}
    stmt = stmt.on_conflict_do_update(index_elements=["id"], set_=update_cols)
    session.execute(stmt)
    session.commit()
    return len(rows)


def main():
    parser = argparse.ArgumentParser(description="Load games from raw schedule data.")
    parser.add_argument("--data-dir", required=True, help="Season data directory, e.g. data/raw/2025")
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    session = SessionLocal()

    game_count = load_games(session, data_dir / "schedule.json")
    print(f"Loaded {game_count} games")

    session.close()


if __name__ == "__main__":
    main()
