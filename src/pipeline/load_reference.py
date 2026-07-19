"""
load_reference.py

Loads venues, teams, and players. Must run before load_games (games.venue_id/
home_team_id/away_team_id are NOT NULL foreign keys) and before load_games or
load_playbyplay touch anything with a player_id foreign key.

Venues come from venues.json (fetched separately via mlb_stats_api.py --with-venues).
Teams and players come from scanning every boxscore file, since schedule.json's
team objects are too sparse (no abbreviation, league, division) to satisfy the
teams table's constraints.
"""

import argparse
import json
from pathlib import Path

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from db.base import SessionLocal
from db.models import Player, Team, Venue


def load_venues(session: Session, venues_path: Path) -> int:
    venues_data = json.loads(venues_path.read_text())
    rows = []
    for v in venues_data:
        location = v.get("location", {})
        coords = location.get("defaultCoordinates", {})
        field_info = v.get("fieldInfo", {})
        rows.append({
            "id": v["id"],
            "name": v["name"],
            "city": location.get("city"),
            "state": location.get("state"),
            "postal_code": location.get("postalCode"),
            "latitude": coords.get("latitude"),
            "longitude": coords.get("longitude"),
            "azimuth_angle": location.get("azimuthAngle"),
            "elevation": location.get("elevation"),
            "time_zone": v.get("timeZone", {}).get("id"),
            "capacity": field_info.get("capacity"),
            "turf_type": field_info.get("turfType"),
            "roof_type": field_info.get("roofType"),
            "left_line": field_info.get("leftLine"),
            "left_center": field_info.get("leftCenter"),
            "center": field_info.get("center"),
            "right_center": field_info.get("rightCenter"),
            "right_line": field_info.get("rightLine"),
        })

    stmt = pg_insert(Venue).values(rows)
    stmt = stmt.on_conflict_do_nothing(index_elements=["id"])
    session.execute(stmt)
    session.commit()
    return len(rows)


def _team_row(team: dict) -> dict:
    return {
        "id": team["id"],
        "name": team["name"],
        "team_name": team.get("teamName"),
        "location_name": team.get("locationName"),
        "abbreviation": team["abbreviation"],
        "team_code": team.get("teamCode"),
        "league_id": team.get("league", {}).get("id"),
        "league_name": team.get("league", {}).get("name"),
        "division_id": team.get("division", {}).get("id"),
        "division_name": team.get("division", {}).get("name"),
        "first_year_of_play": team.get("firstYearOfPlay"),
        "active": team.get("active", True),
    }


def _player_row(person: dict) -> dict:
    return {
        "id": person["id"],
        "full_name": person["fullName"],
        "boxscore_name": person.get("boxscoreName"),
    }


def load_teams_and_players(session: Session, boxscore_dir: Path) -> tuple[int, int]:
    teams: dict[int, dict] = {}
    players: dict[int, dict] = {}

    for path in boxscore_dir.glob("*.json"):
        box = json.loads(path.read_text())
        for side in ("home", "away"):
            team_side = box["teams"][side]
            team = team_side["team"]
            teams[team["id"]] = _team_row(team)
            for player in team_side["players"].values():
                person = player["person"]
                players[person["id"]] = _player_row(person)

    if teams:
        stmt = pg_insert(Team).values(list(teams.values()))
        stmt = stmt.on_conflict_do_nothing(index_elements=["id"])
        session.execute(stmt)

    if players:
        stmt = pg_insert(Player).values(list(players.values()))
        stmt = stmt.on_conflict_do_nothing(index_elements=["id"])
        session.execute(stmt)

    session.commit()
    return len(teams), len(players)


def main():
    parser = argparse.ArgumentParser(description="Load venues, teams, and players from raw data.")
    parser.add_argument("--data-dir", required=True, help="Season data directory, e.g. data/raw/2025")
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    session = SessionLocal()

    venue_count = load_venues(session, data_dir / "venues.json")
    print(f"Loaded {venue_count} venues")

    team_count, player_count = load_teams_and_players(session, data_dir / "boxscores")
    print(f"Loaded {team_count} teams, {player_count} players")

    session.close()


if __name__ == "__main__":
    main()
