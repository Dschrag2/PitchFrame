from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models import Player
from db.stats_views import player_season_batting_stats, player_season_pitching_stats

from dependencies import get_db
from schemas.leaderboards import LeaderboardEntry
from schemas.players import PlayerSummary

router = APIRouter(prefix="/leaderboards", tags=["leaderboards"])

BATTING_STATS = {
    "home_runs", "hits", "rbi", "runs", "stolen_bases", "doubles", "triples",
    "base_on_balls", "strike_outs", "avg", "obp", "slg", "ops",
}
PITCHING_STATS = {"wins", "strike_outs", "saves", "era", "whip", "k_per_9", "bb_per_9"}
LOWER_IS_BETTER = {"era", "whip", "bb_per_9"}


def _dedupe_by_player(rows, qualifier_col: str):
    """Season views carry one row per team a player appeared for, plus a combined
    'all teams' row (team_id NULL) when they were traded. Keep whichever row has
    the larger qualifier value per player — that's always the combined row when
    one exists, since it's a sum of the per-team rows."""
    best: dict[int, object] = {}
    for row in rows:
        existing = best.get(row.player_id)
        if existing is None or getattr(row, qualifier_col) > getattr(existing, qualifier_col):
            best[row.player_id] = row
    return list(best.values())


@router.get("/batting", response_model=list[LeaderboardEntry])
def batting_leaderboard(
    season: int = Query(...),
    stat: str = Query(..., description=f"One of: {sorted(BATTING_STATS)}"),
    limit: int = Query(10, le=50),
    min_at_bats: int = Query(100, description="Minimum at-bats to qualify"),
    db: Session = Depends(get_db),
):
    if stat not in BATTING_STATS:
        raise HTTPException(status_code=400, detail=f"stat must be one of {sorted(BATTING_STATS)}")

    view = player_season_batting_stats
    stmt = select(view).where(view.c.season == season, view.c.at_bats >= min_at_bats)
    rows = _dedupe_by_player(db.execute(stmt).all(), "at_bats")

    return _build_leaderboard(db, rows, stat, limit, games_col="games_played")


@router.get("/pitching", response_model=list[LeaderboardEntry])
def pitching_leaderboard(
    season: int = Query(...),
    stat: str = Query(..., description=f"One of: {sorted(PITCHING_STATS)}"),
    limit: int = Query(10, le=50),
    min_outs: int = Query(30, description="Minimum outs recorded to qualify (30 outs = 10 innings)"),
    db: Session = Depends(get_db),
):
    if stat not in PITCHING_STATS:
        raise HTTPException(status_code=400, detail=f"stat must be one of {sorted(PITCHING_STATS)}")

    view = player_season_pitching_stats
    stmt = select(view).where(view.c.season == season, view.c.outs >= min_outs)
    rows = _dedupe_by_player(db.execute(stmt).all(), "outs")

    return _build_leaderboard(db, rows, stat, limit, games_col="games_played")


def _build_leaderboard(db: Session, rows: list, stat: str, limit: int, games_col: str) -> list[LeaderboardEntry]:
    reverse = stat not in LOWER_IS_BETTER
    rows = [r for r in rows if getattr(r, stat) is not None]
    rows.sort(key=lambda r: getattr(r, stat), reverse=reverse)
    top_rows = rows[:limit]

    player_ids = [r.player_id for r in top_rows]
    players = {p.id: p for p in db.execute(select(Player).where(Player.id.in_(player_ids))).scalars()}

    entries = []
    for i, row in enumerate(top_rows, start=1):
        player = players[row.player_id]
        entries.append(
            LeaderboardEntry(
                rank=i,
                player=PlayerSummary(id=player.id, full_name=player.full_name, boxscore_name=player.boxscore_name),
                value=float(getattr(row, stat)),
                games_played=getattr(row, games_col),
            )
        )
    return entries
