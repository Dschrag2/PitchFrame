"""
load_playbyplay.py

Loads at_bats, events, pitches, batted_balls, baserunning_events, and
baserunning_event_credits from play-by-play JSON. Requires games, teams,
and players to already exist.

Processes one game at a time (not the whole season in memory) so a failure
partway through doesn't lose prior progress, and re-running is safe since
every insert is an upsert.
"""

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from db.base import SessionLocal
from db.models import AtBat, BaserunningEvent, BaserunningEventCredit, BattedBall, Event, Pitch, Player

CHUNK_SIZE = 500

HIT_EVENT_TYPES = {"single", "double", "triple", "home_run"}
BASES_BY_HIT_TYPE = {"single": 1, "double": 2, "triple": 3, "home_run": 4}
WALK_EVENT_TYPES = {"walk", "intent_walk"}
STRIKEOUT_EVENT_TYPES = {"strikeout", "strikeout_double_play"}
SAC_FLY_EVENT_TYPES = {"sac_fly", "sac_fly_double_play"}
SAC_BUNT_EVENT_TYPES = {"sac_bunt", "sac_bunt_double_play"}
# Plate appearances that end via a baserunning out (caught stealing, pickoff) rather
# than a batting decision, plus the standard non-AB categories (walks, HBP, sacrifices,
# interference). Everything else defaults to counting as an official at-bat.
NON_AT_BAT_EVENT_TYPES = WALK_EVENT_TYPES | SAC_FLY_EVENT_TYPES | SAC_BUNT_EVENT_TYPES | {
    "hit_by_pitch", "catcher_interf", "batter_interference", "fan_interference", "no_pitch",
}


def _parse_dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _outcome_flags(event_type: str) -> dict:
    is_baserunning_only = event_type.startswith("caught_stealing") or event_type.startswith("pickoff")
    return {
        "is_hit": event_type in HIT_EVENT_TYPES,
        "is_walk": event_type in WALK_EVENT_TYPES,
        "is_hit_by_pitch": event_type == "hit_by_pitch",
        "is_strikeout": event_type in STRIKEOUT_EVENT_TYPES,
        "is_sac_fly": event_type in SAC_FLY_EVENT_TYPES,
        "is_sac_bunt": event_type in SAC_BUNT_EVENT_TYPES,
        "is_at_bat": not (is_baserunning_only or event_type in NON_AT_BAT_EVENT_TYPES),
        "bases": BASES_BY_HIT_TYPE.get(event_type, 0),
    }


def _at_bat_row(game_id: int, play: dict) -> dict:
    about = play["about"]
    matchup = play["matchup"]
    result = play["result"]
    event_type = result.get("eventType") or ""
    return {
        "game_id": game_id,
        "at_bat_index": about["atBatIndex"],
        "inning": about["inning"],
        "half_inning": "bot" if about["halfInning"] == "bottom" else "top",
        "batter_id": matchup["batter"]["id"],
        "pitcher_id": matchup["pitcher"]["id"],
        "bat_side": matchup["batSide"]["code"],
        "pitch_hand": matchup["pitchHand"]["code"],
        "event": result.get("event") or "",
        "event_type": event_type,
        "description": result.get("description") or "",
        "rbi": result.get("rbi") or 0,
        "is_scoring_play": bool(about.get("isScoringPlay")),
        "is_out": bool(result.get("isOut")),
        "home_score": result.get("homeScore") or 0,
        "away_score": result.get("awayScore") or 0,
        "start_time": _parse_dt(about["startTime"]),
        "end_time": _parse_dt(about["endTime"]) if about.get("endTime") else None,
        **_outcome_flags(event_type),
    }


def _event_row(
    game_id: int, at_bat_index: int, e: dict, global_sequence: int,
    home_score: int, away_score: int, known_player_ids: set,
) -> dict:
    details = e.get("details", {})
    event_code = details.get("eventType") or details.get("code") or e["type"]
    event_name = details.get("event") or details.get("description") or e["type"]
    player = e.get("player") or {}
    return {
        "game_id": game_id,
        "at_bat_index": at_bat_index,
        "event_index": e["index"],
        "global_sequence": global_sequence,
        "event_type": e["type"],
        "is_pitch": bool(e.get("isPitch")),
        "event_code": event_code,
        "event_name": event_name,
        "description": details.get("description") or event_name,
        "start_time": _parse_dt(e["startTime"]),
        "end_time": _parse_dt(e["endTime"]) if e.get("endTime") else None,
        "home_score": home_score,
        "away_score": away_score,
        "related_player_id": player.get("id") if player.get("id") in known_player_ids else None,
    }


def _pitch_row(game_id: int, at_bat_index: int, e: dict, batter_id: int, pitcher_id: int) -> dict:
    details = e.get("details", {})
    count = e.get("count", {})
    pitch_data = e.get("pitchData", {})
    coords = pitch_data.get("coordinates", {})
    breaks = pitch_data.get("breaks", {})
    pitch_type = details.get("type", {})
    call = details.get("call", {})
    return {
        "game_id": game_id,
        "at_bat_index": at_bat_index,
        "event_index": e["index"],
        "batter_id": batter_id,
        "pitcher_id": pitcher_id,
        "pitch_number": e.get("pitchNumber") or 0,
        "balls": count.get("balls") or 0,
        "strikes": count.get("strikes") or 0,
        "outs": count.get("outs") or 0,
        "pitch_type_code": pitch_type.get("code"),
        "pitch_type_description": pitch_type.get("description"),
        "call_code": call.get("code") or "",
        "call_description": call.get("description") or "",
        "is_strike": bool(details.get("isStrike")),
        "is_ball": bool(details.get("isBall")),
        "is_in_play": bool(details.get("isInPlay")),
        "start_speed": pitch_data.get("startSpeed"),
        "end_speed": pitch_data.get("endSpeed"),
        "spin_rate": breaks.get("spinRate"),
        "spin_direction": breaks.get("spinDirection"),
        "break_angle": breaks.get("breakAngle"),
        "break_length": breaks.get("breakLength"),
        "break_vertical": breaks.get("breakVertical"),
        "break_vertical_induced": breaks.get("breakVerticalInduced"),
        "break_horizontal": breaks.get("breakHorizontal"),
        "zone": pitch_data.get("zone"),
        "type_confidence": pitch_data.get("typeConfidence"),
        "plate_time": pitch_data.get("plateTime"),
        "extension": pitch_data.get("extension"),
        "strike_zone_top": pitch_data.get("strikeZoneTop"),
        "strike_zone_bottom": pitch_data.get("strikeZoneBottom"),
        "plate_x": coords.get("pX"),
        "plate_z": coords.get("pZ"),
        "release_pos_x": coords.get("x0"),
        "release_pos_y": coords.get("y0"),
        "release_pos_z": coords.get("z0"),
        "vx0": coords.get("vX0"),
        "vy0": coords.get("vY0"),
        "vz0": coords.get("vZ0"),
        "ax": coords.get("aX"),
        "ay": coords.get("aY"),
        "az": coords.get("aZ"),
        "pfx_x": coords.get("pfxX"),
        "pfx_z": coords.get("pfxZ"),
        "play_id": e.get("playId"),
    }


def _batted_ball_row(game_id: int, at_bat_index: int, e: dict) -> dict:
    hit_data = e.get("hitData", {})
    coords = hit_data.get("coordinates", {})
    return {
        "game_id": game_id,
        "at_bat_index": at_bat_index,
        "event_index": e["index"],
        "launch_speed": hit_data.get("launchSpeed"),
        "launch_angle": hit_data.get("launchAngle"),
        "total_distance": hit_data.get("totalDistance"),
        "trajectory": hit_data.get("trajectory"),
        "hardness": hit_data.get("hardness"),
        "location": hit_data.get("location"),
        "coord_x": coords.get("coordX"),
        "coord_y": coords.get("coordY"),
    }


def _baserunning_row(game_id: int, at_bat_index: int, runner: dict, movement_index: int) -> dict:
    movement = runner["movement"]
    details = runner["details"]
    responsible_pitcher = details.get("responsiblePitcher")
    return {
        "game_id": game_id,
        "at_bat_index": at_bat_index,
        "event_index": details["playIndex"],
        "runner_id": details["runner"]["id"],
        "movement_index": movement_index,
        "origin_base": movement.get("originBase"),
        "start_base": movement.get("start"),
        "end_base": movement.get("end"),
        "out_base": movement.get("outBase"),
        "is_out": bool(movement.get("isOut")),
        "out_number": movement.get("outNumber"),
        "movement_reason": details.get("movementReason"),
        "responsible_pitcher_id": responsible_pitcher["id"] if responsible_pitcher else None,
        "is_scoring_event": bool(details.get("isScoringEvent")),
        "rbi": bool(details.get("rbi")),
        "earned": bool(details.get("earned")),
        "team_unearned": bool(details.get("teamUnearned")),
    }


def _baserunning_credit_row(
    game_id: int, at_bat_index: int, runner: dict, movement_index: int, credit_index: int, credit: dict
) -> dict:
    position = credit["position"]
    return {
        "game_id": game_id,
        "at_bat_index": at_bat_index,
        "event_index": runner["details"]["playIndex"],
        "runner_id": runner["details"]["runner"]["id"],
        "movement_index": movement_index,
        "credit_index": credit_index,
        "player_id": credit["player"]["id"],
        "position_code": position["code"],
        "position_name": position["name"],
        "position_abbreviation": position["abbreviation"],
        "credit_type": credit["credit"],
    }


def _resolve_batter_for_at_bat(play: dict, sub_events: list[dict]) -> int:
    if sub_events:
        first_sub = sub_events[0]
        replaced = first_sub.get("replacedPlayer")
        if replaced:
            return replaced["id"]
    return play["matchup"]["batter"]["id"]


def _process_game(game_id: int, pbp_data: dict, known_player_ids: set) -> dict:
    plays = pbp_data["liveData"]["plays"]["allPlays"]

    rows = {
        "at_bats": [], "events": [], "pitches": [], "batted_balls": [],
        "baserunning_events": [], "baserunning_event_credits": [],
    }

    global_sequence = 0
    current_pitcher_id: Optional[int] = None
    home_score = 0
    away_score = 0

    for play in plays:
        at_bat_index = play["about"]["atBatIndex"]
        rows["at_bats"].append(_at_bat_row(game_id, play))

        events = sorted(play["playEvents"], key=lambda e: e["index"])
        offensive_subs = [
            e for e in events if e.get("details", {}).get("eventType") == "offensive_substitution"
        ]
        current_batter_id = _resolve_batter_for_at_bat(play, offensive_subs)
        if current_pitcher_id is None:
            current_pitcher_id = play["matchup"]["pitcher"]["id"]

        for e in events:
            details = e.get("details", {})
            event_type_detail = details.get("eventType")
            if event_type_detail == "offensive_substitution":
                current_batter_id = e["player"]["id"]
            elif event_type_detail == "pitching_substitution":
                current_pitcher_id = e["player"]["id"]

            if "homeScore" in details:
                home_score = details["homeScore"]
            if "awayScore" in details:
                away_score = details["awayScore"]

            rows["events"].append(
                _event_row(game_id, at_bat_index, e, global_sequence, home_score, away_score, known_player_ids)
            )
            global_sequence += 1

            if e.get("isPitch"):
                rows["pitches"].append(_pitch_row(game_id, at_bat_index, e, current_batter_id, current_pitcher_id))
                if "hitData" in e:
                    rows["batted_balls"].append(_batted_ball_row(game_id, at_bat_index, e))

        movement_counts: dict[tuple, int] = {}
        for runner in play.get("runners", []):
            details = runner["details"]
            leg_key = (details["playIndex"], details["runner"]["id"])
            movement_index = movement_counts.get(leg_key, 0)
            movement_counts[leg_key] = movement_index + 1

            rows["baserunning_events"].append(_baserunning_row(game_id, at_bat_index, runner, movement_index))
            for credit_index, credit in enumerate(runner.get("credits", [])):
                rows["baserunning_event_credits"].append(
                    _baserunning_credit_row(game_id, at_bat_index, runner, movement_index, credit_index, credit)
                )

    return rows


def _chunked(items: list, size: int = CHUNK_SIZE):
    for i in range(0, len(items), size):
        yield items[i : i + size]


def _upsert(session: Session, model, rows: list[dict], pk_cols: list[str]) -> None:
    if not rows:
        return
    update_cols = [c.name for c in model.__table__.columns if c.name not in pk_cols]
    for chunk in _chunked(rows):
        stmt = pg_insert(model).values(chunk)
        set_ = {col: getattr(stmt.excluded, col) for col in update_cols}
        stmt = stmt.on_conflict_do_update(index_elements=pk_cols, set_=set_)
        session.execute(stmt)


def load_playbyplay(session: Session, pbp_dir: Path) -> dict:
    totals = {k: 0 for k in ["at_bats", "events", "pitches", "batted_balls", "baserunning_events", "baserunning_event_credits"]}
    paths = sorted(pbp_dir.glob("*.json"))
    known_player_ids = set(session.execute(select(Player.id)).scalars())

    for i, path in enumerate(paths, start=1):
        game_id = int(path.stem)
        try:
            pbp_data = json.loads(path.read_text())
            rows = _process_game(game_id, pbp_data, known_player_ids)

            _upsert(session, AtBat, rows["at_bats"], ["game_id", "at_bat_index"])
            _upsert(session, Event, rows["events"], ["game_id", "at_bat_index", "event_index"])
            _upsert(session, Pitch, rows["pitches"], ["game_id", "at_bat_index", "event_index"])
            _upsert(session, BattedBall, rows["batted_balls"], ["game_id", "at_bat_index", "event_index"])
            _upsert(
                session, BaserunningEvent, rows["baserunning_events"],
                ["game_id", "at_bat_index", "event_index", "runner_id", "movement_index"],
            )
            _upsert(
                session, BaserunningEventCredit, rows["baserunning_event_credits"],
                ["game_id", "at_bat_index", "event_index", "runner_id", "movement_index", "credit_index"],
            )
            session.commit()

            for key in totals:
                totals[key] += len(rows[key])
            print(f"[{i}/{len(paths)}] gamePk={game_id}: {len(rows['pitches'])} pitches, {len(rows['at_bats'])} at-bats")
        except Exception as e:
            session.rollback()
            print(f"[{i}/{len(paths)}] FAILED gamePk={game_id}: {e}")

    return totals


def main():
    parser = argparse.ArgumentParser(description="Load play-by-play data from raw data.")
    parser.add_argument("--data-dir", required=True, help="Season data directory, e.g. data/raw/2025")
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    session = SessionLocal()

    totals = load_playbyplay(session, data_dir / "play_by_play")
    print(totals)

    session.close()


if __name__ == "__main__":
    main()
