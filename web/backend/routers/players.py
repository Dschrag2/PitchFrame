from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models import Player
from db.stats_views import (
    player_career_batting_stats,
    player_career_pitching_stats,
    player_postseason_batting_stats,
    player_postseason_pitching_stats,
    player_season_batting_stats,
    player_season_pitching_stats,
)

from dependencies import get_db
from schemas.players import (
    BattingStatsResponse,
    CareerBattingStats,
    CareerPitchingStats,
    PitchingStatsResponse,
    PlayerSummary,
    SeasonBattingStats,
    SeasonPitchingStats,
)

router = APIRouter(prefix="/players", tags=["players"])


def _format_innings_pitched(outs: int) -> str:
    return f"{outs // 3}.{outs % 3}"


def _player_summary(player: Player) -> PlayerSummary:
    return PlayerSummary(id=player.id, full_name=player.full_name, boxscore_name=player.boxscore_name)


def _get_player_or_404(db: Session, player_id: int) -> Player:
    player = db.get(Player, player_id)
    if player is None:
        raise HTTPException(status_code=404, detail=f"Player {player_id} not found")
    return player


@router.get("", response_model=list[PlayerSummary])
def search_players(
    q: str = Query(..., min_length=2, description="Search players by name"),
    limit: int = Query(25, le=100),
    db: Session = Depends(get_db),
):
    stmt = select(Player).where(Player.full_name.ilike(f"%{q}%")).order_by(Player.full_name).limit(limit)
    players = db.execute(stmt).scalars().all()
    return [_player_summary(p) for p in players]


@router.get("/{player_id}", response_model=PlayerSummary)
def get_player(player_id: int, db: Session = Depends(get_db)):
    return _player_summary(_get_player_or_404(db, player_id))


@router.get("/{player_id}/batting-stats", response_model=BattingStatsResponse)
def get_batting_stats(player_id: int, db: Session = Depends(get_db)):
    player = _get_player_or_404(db, player_id)

    seasons = db.execute(
        select(player_season_batting_stats)
        .where(player_season_batting_stats.c.player_id == player_id)
        .order_by(player_season_batting_stats.c.season)
    ).all()
    postseason = db.execute(
        select(player_postseason_batting_stats)
        .where(player_postseason_batting_stats.c.player_id == player_id)
        .order_by(player_postseason_batting_stats.c.season)
    ).all()
    career = db.execute(
        select(player_career_batting_stats).where(player_career_batting_stats.c.player_id == player_id)
    ).first()

    return BattingStatsResponse(
        player=_player_summary(player),
        seasons=[SeasonBattingStats(**row._mapping) for row in seasons],
        postseason=[SeasonBattingStats(**row._mapping) for row in postseason],
        career=CareerBattingStats(**career._mapping) if career else None,
    )


@router.get("/{player_id}/pitching-stats", response_model=PitchingStatsResponse)
def get_pitching_stats(player_id: int, db: Session = Depends(get_db)):
    player = _get_player_or_404(db, player_id)

    def _pitching_row(row) -> dict:
        data = dict(row._mapping)
        data["innings_pitched"] = _format_innings_pitched(data.pop("outs"))
        return data

    seasons = db.execute(
        select(player_season_pitching_stats)
        .where(player_season_pitching_stats.c.player_id == player_id)
        .order_by(player_season_pitching_stats.c.season)
    ).all()
    postseason = db.execute(
        select(player_postseason_pitching_stats)
        .where(player_postseason_pitching_stats.c.player_id == player_id)
        .order_by(player_postseason_pitching_stats.c.season)
    ).all()
    career = db.execute(
        select(player_career_pitching_stats).where(player_career_pitching_stats.c.player_id == player_id)
    ).first()

    return PitchingStatsResponse(
        player=_player_summary(player),
        seasons=[SeasonPitchingStats(**_pitching_row(row)) for row in seasons],
        postseason=[SeasonPitchingStats(**_pitching_row(row)) for row in postseason],
        career=CareerPitchingStats(**_pitching_row(career)) if career else None,
    )
