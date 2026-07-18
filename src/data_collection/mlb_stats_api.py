"""
mlb_stats_api.py

Pulls schedule, box score, and play-by-play data from the free MLB Stats API
(https://statsapi.mlb.com). No API key required.

Usage:
    # Pull a full season (regular + postseason by default)
    python mlb_stats_api.py --season 2025 --with-boxscores --with-play-by-play --out ../../data/raw

    # Pull a narrow date range instead (e.g. for a quick incremental/daily update)
    python mlb_stats_api.py --start 2025-04-01 --end 2025-04-07 --out ../../data/raw

Re-running is safe: existing files are skipped unless --overwrite is passed, so an
interrupted season pull can just be re-run to pick up where it left off.
"""

import argparse
import json
import time
from pathlib import Path

import requests

BASE_URL = "https://statsapi.mlb.com/api/v1"
# The live/play-by-play feed endpoint is only served under the v1.1 API, not v1.
BASE_URL_V1_1 = "https://statsapi.mlb.com/api/v1.1"
SPORT_ID_MLB = 1

# Regular season, wild card, division series, league championship, world series.
# Excludes spring training ("S") since exhibition games aren't useful for modeling.
DEFAULT_GAME_TYPES = "R,F,D,L,W"


def get_schedule(start_date: str, end_date: str) -> list[dict]:
    """Fetch all MLB games scheduled between start_date and end_date (YYYY-MM-DD)."""
    params = {
        "sportId": SPORT_ID_MLB,
        "startDate": start_date,
        "endDate": end_date,
    }
    resp = requests.get(f"{BASE_URL}/schedule", params=params, timeout=30)
    resp.raise_for_status()
    return _flatten_schedule(resp.json())


def get_season_schedule(season: int, game_types: str = DEFAULT_GAME_TYPES) -> list[dict]:
    """Fetch every game for a given season, optionally filtered to specific game types.

    game_types is a comma-separated list of MLB Stats API game type codes, e.g.
    "R" (regular season), "F" (wild card), "D" (division series), "L" (league
    championship series), "W" (world series), "S" (spring training).
    """
    params = {
        "sportId": SPORT_ID_MLB,
        "season": season,
        "gameType": game_types,
    }
    resp = requests.get(f"{BASE_URL}/schedule", params=params, timeout=30)
    resp.raise_for_status()
    return _flatten_schedule(resp.json())


def _flatten_schedule(data: dict) -> list[dict]:
    games = []
    for date_entry in data.get("dates", []):
        games.extend(date_entry.get("games", []))
    return games


def get_boxscore(game_pk: int) -> dict:
    """Fetch the full boxscore for a single game by its gamePk id."""
    resp = requests.get(f"{BASE_URL}/game/{game_pk}/boxscore", timeout=30)
    resp.raise_for_status()
    return resp.json()


def get_live_feed(game_pk: int) -> dict:
    """Fetch the live/play-by-play feed for a single game (works for completed games too)."""
    resp = requests.get(f"{BASE_URL_V1_1}/game/{game_pk}/feed/live", timeout=30)
    resp.raise_for_status()
    return resp.json()


def save_json(obj: dict | list, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(obj, f, indent=2)


def fetch_per_game_data(
    games: list[dict],
    out_dir: Path,
    sleep: float,
    overwrite: bool,
    with_boxscores: bool,
    with_play_by_play: bool,
) -> None:
    total = len(games)
    for i, game in enumerate(games, start=1):
        game_pk = game["gamePk"]

        if with_boxscores:
            box_path = out_dir / "boxscores" / f"{game_pk}.json"
            if box_path.exists() and not overwrite:
                print(f"[{i}/{total}] boxscore for gamePk={game_pk} already exists, skipping")
            else:
                print(f"[{i}/{total}] Fetching boxscore for gamePk={game_pk}")
                try:
                    save_json(get_boxscore(game_pk), box_path)
                except requests.exceptions.RequestException as e:
                    print(f"  Failed boxscore for {game_pk}: {e}")
                time.sleep(sleep)  # be polite to the API

        if with_play_by_play:
            pbp_path = out_dir / "play_by_play" / f"{game_pk}.json"
            if pbp_path.exists() and not overwrite:
                print(f"[{i}/{total}] play-by-play for gamePk={game_pk} already exists, skipping")
            else:
                print(f"[{i}/{total}] Fetching play-by-play for gamePk={game_pk}")
                try:
                    save_json(get_live_feed(game_pk), pbp_path)
                except requests.exceptions.RequestException as e:
                    print(f"  Failed play-by-play for {game_pk}: {e}")
                time.sleep(sleep)  # be polite to the API


def main():
    parser = argparse.ArgumentParser(description="Pull MLB Stats API data for a season or date range.")
    parser.add_argument("--season", type=int, help="Season year, e.g. 2025. Fetches the full season schedule.")
    parser.add_argument("--start", help="Start date, YYYY-MM-DD (alternative to --season)")
    parser.add_argument("--end", help="End date, YYYY-MM-DD (alternative to --season)")
    parser.add_argument(
        "--game-types",
        default=DEFAULT_GAME_TYPES,
        help=f"Comma-separated MLB game type codes to include with --season (default: {DEFAULT_GAME_TYPES})",
    )
    parser.add_argument("--out", default="../../data/raw", help="Output directory")
    parser.add_argument(
        "--with-boxscores",
        action="store_true",
        help="Also fetch boxscore data for each game (one request per game)",
    )
    parser.add_argument(
        "--with-play-by-play",
        action="store_true",
        help="Also fetch the play-by-play live feed for each game (one request per game)",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Re-fetch and overwrite files that already exist on disk (default: skip them)",
    )
    parser.add_argument("--sleep", type=float, default=0.5, help="Seconds to sleep between per-game requests")
    args = parser.parse_args()

    if args.season is None and (args.start is None or args.end is None):
        parser.error("either --season, or both --start and --end, are required")

    if args.season is not None:
        out_dir = Path(args.out) / str(args.season)
        games = get_season_schedule(args.season, args.game_types)
        print(f"Found {len(games)} games for the {args.season} season (game types: {args.game_types})")
        save_json(games, out_dir / "schedule.json")
    else:
        out_dir = Path(args.out)
        games = get_schedule(args.start, args.end)
        print(f"Found {len(games)} games between {args.start} and {args.end}")
        save_json(games, out_dir / f"schedule_{args.start}_to_{args.end}.json")

    if args.with_boxscores or args.with_play_by_play:
        fetch_per_game_data(
            games,
            out_dir,
            sleep=args.sleep,
            overwrite=args.overwrite,
            with_boxscores=args.with_boxscores,
            with_play_by_play=args.with_play_by_play,
        )

    print("Done.")


if __name__ == "__main__":
    main()
