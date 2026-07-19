"""
load_boxscores.py

Loads batting_boxscores and pitching_boxscores from boxscore JSON files.
Requires games, teams, and players to already exist.
"""

import argparse
import json
from pathlib import Path
from typing import Optional

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from db.base import SessionLocal
from db.models import BattingBoxscore, PitchingBoxscore

CHUNK_SIZE = 500

BATTING_STAT_FIELDS = {
    "games_played": "gamesPlayed",
    "fly_outs": "flyOuts",
    "ground_outs": "groundOuts",
    "air_outs": "airOuts",
    "runs": "runs",
    "doubles": "doubles",
    "triples": "triples",
    "home_runs": "homeRuns",
    "strike_outs": "strikeOuts",
    "base_on_balls": "baseOnBalls",
    "intentional_walks": "intentionalWalks",
    "hits": "hits",
    "hit_by_pitch": "hitByPitch",
    "at_bats": "atBats",
    "caught_stealing": "caughtStealing",
    "stolen_bases": "stolenBases",
    "ground_into_double_play": "groundIntoDoublePlay",
    "ground_into_triple_play": "groundIntoTriplePlay",
    "plate_appearances": "plateAppearances",
    "total_bases": "totalBases",
    "rbi": "rbi",
    "left_on_base": "leftOnBase",
    "sac_bunts": "sacBunts",
    "sac_flies": "sacFlies",
    "catchers_interference": "catchersInterference",
    "pickoffs": "pickoffs",
    "pop_outs": "popOuts",
    "line_outs": "lineOuts",
}

PITCHING_STAT_FIELDS = {
    "games_played": "gamesPlayed",
    "games_started": "gamesStarted",
    "fly_outs": "flyOuts",
    "ground_outs": "groundOuts",
    "air_outs": "airOuts",
    "runs": "runs",
    "doubles": "doubles",
    "triples": "triples",
    "home_runs": "homeRuns",
    "strike_outs": "strikeOuts",
    "base_on_balls": "baseOnBalls",
    "intentional_walks": "intentionalWalks",
    "hits": "hits",
    "hit_by_pitch": "hitByPitch",
    "at_bats": "atBats",
    "caught_stealing": "caughtStealing",
    "stolen_bases": "stolenBases",
    "number_of_pitches": "numberOfPitches",
    "outs": "outs",
    "wins": "wins",
    "losses": "losses",
    "saves": "saves",
    "save_opportunities": "saveOpportunities",
    "holds": "holds",
    "blown_saves": "blownSaves",
    "earned_runs": "earnedRuns",
    "batters_faced": "battersFaced",
    "games_pitched": "gamesPitched",
    "complete_games": "completeGames",
    "shutouts": "shutouts",
    "pitches_thrown": "pitchesThrown",
    "balls": "balls",
    "strikes": "strikes",
    "hit_batsmen": "hitBatsmen",
    "balks": "balks",
    "wild_pitches": "wildPitches",
    "pickoffs": "pickoffs",
    "rbi": "rbi",
    "games_finished": "gamesFinished",
    "inherited_runners": "inheritedRunners",
    "inherited_runners_scored": "inheritedRunnersScored",
    "catchers_interference": "catchersInterference",
    "sac_bunts": "sacBunts",
    "sac_flies": "sacFlies",
    "passed_ball": "passedBall",
    "pop_outs": "popOuts",
    "line_outs": "lineOuts",
}


def _parse_rate(value) -> Optional[float]:
    """MLB reports rate stats (stolenBasePercentage, atBatsPerHomeRun, etc.) as
    strings that can be placeholders like '.---' or '-.--' when undefined."""
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _position_fields(player: dict) -> dict:
    position = player["position"]
    return {
        "position_code": position["code"],
        "position_name": position["name"],
        "position_abbreviation": position["abbreviation"],
        "jersey_number": player.get("jerseyNumber"),
    }


def _batting_row(game_id: int, team_id: int, player: dict) -> dict:
    stats = player["stats"]["batting"]
    row = {
        "game_id": game_id,
        "player_id": player["person"]["id"],
        "team_id": team_id,
        **_position_fields(player),
        "stolen_base_percentage": _parse_rate(stats.get("stolenBasePercentage")),
        "at_bats_per_home_run": _parse_rate(stats.get("atBatsPerHomeRun")),
        "summary": stats.get("summary"),
    }
    for db_col, mlb_key in BATTING_STAT_FIELDS.items():
        row[db_col] = stats.get(mlb_key, 0)
    return row


def _pitching_row(game_id: int, team_id: int, player: dict) -> dict:
    stats = player["stats"]["pitching"]
    row = {
        "game_id": game_id,
        "player_id": player["person"]["id"],
        "team_id": team_id,
        **_position_fields(player),
        "stolen_base_percentage": _parse_rate(stats.get("stolenBasePercentage")),
        "strike_percentage": _parse_rate(stats.get("strikePercentage")),
        "runs_scored_per9": _parse_rate(stats.get("runsScoredPer9")),
        "home_runs_per9": _parse_rate(stats.get("homeRunsPer9")),
        "innings_pitched": stats.get("inningsPitched", "0.0"),
        "note": stats.get("note"),
        "summary": stats.get("summary"),
    }
    for db_col, mlb_key in PITCHING_STAT_FIELDS.items():
        row[db_col] = stats.get(mlb_key, 0)
    return row


def _chunked(rows: list[dict], size: int = CHUNK_SIZE):
    for i in range(0, len(rows), size):
        yield rows[i : i + size]


def _upsert(session: Session, model, rows: list[dict], pk_cols: list[str]) -> None:
    if not rows:
        return
    update_cols = {c.name: None for c in model.__table__.columns if c.name not in pk_cols}
    for chunk in _chunked(rows):
        stmt = pg_insert(model).values(chunk)
        set_ = {col: getattr(stmt.excluded, col) for col in update_cols}
        stmt = stmt.on_conflict_do_update(index_elements=pk_cols, set_=set_)
        session.execute(stmt)


def load_boxscores(session: Session, boxscore_dir: Path) -> tuple[int, int]:
    batting_rows = []
    pitching_rows = []

    for path in boxscore_dir.glob("*.json"):
        game_id = int(path.stem)
        box = json.loads(path.read_text())
        for side in ("home", "away"):
            team_side = box["teams"][side]
            team_id = team_side["team"]["id"]
            for player in team_side["players"].values():
                if player["stats"].get("batting"):
                    batting_rows.append(_batting_row(game_id, team_id, player))
                if player["stats"].get("pitching"):
                    pitching_rows.append(_pitching_row(game_id, team_id, player))

    _upsert(session, BattingBoxscore, batting_rows, ["game_id", "player_id"])
    _upsert(session, PitchingBoxscore, pitching_rows, ["game_id", "player_id"])
    session.commit()
    return len(batting_rows), len(pitching_rows)


def main():
    parser = argparse.ArgumentParser(description="Load boxscores from raw data.")
    parser.add_argument("--data-dir", required=True, help="Season data directory, e.g. data/raw/2025")
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    session = SessionLocal()

    batting_count, pitching_count = load_boxscores(session, data_dir / "boxscores")
    print(f"Loaded {batting_count} batting lines, {pitching_count} pitching lines")

    session.close()


if __name__ == "__main__":
    main()
