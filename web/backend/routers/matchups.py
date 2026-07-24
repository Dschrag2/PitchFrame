from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from db.models import AtBat

from dependencies import get_db
from routers.players import _get_player_or_404, _player_summary
from schemas.matchups import MatchupStats

router = APIRouter(prefix="/players", tags=["matchups"])


@router.get("/{batter_id}/vs/{pitcher_id}", response_model=MatchupStats)
def get_matchup(
    batter_id: int,
    pitcher_id: int,
    season: Optional[int] = Query(None, description="Restrict to one season; omit for the batter's whole career"),
    db: Session = Depends(get_db),
):
    batter = _get_player_or_404(db, batter_id)
    pitcher = _get_player_or_404(db, pitcher_id)

    stmt = select(
        func.count().label("plate_appearances"),
        func.count().filter(AtBat.is_at_bat).label("at_bats"),
        func.count().filter(AtBat.is_hit).label("hits"),
        func.count().filter(AtBat.event_type == "double").label("doubles"),
        func.count().filter(AtBat.event_type == "triple").label("triples"),
        func.count().filter(AtBat.event_type == "home_run").label("home_runs"),
        func.count().filter(AtBat.is_walk).label("walks"),
        func.count().filter(AtBat.is_hit_by_pitch).label("hit_by_pitch"),
        func.count().filter(AtBat.is_strikeout).label("strikeouts"),
        func.coalesce(func.sum(AtBat.rbi), 0).label("rbi"),
    ).where(AtBat.batter_id == batter_id, AtBat.pitcher_id == pitcher_id)

    if season is not None:
        from db.models import Game

        stmt = stmt.join(Game, Game.id == AtBat.game_id).where(Game.season == season)

    row = db.execute(stmt).one()
    avg = round(row.hits / row.at_bats, 3) if row.at_bats else None

    return MatchupStats(
        batter=_player_summary(batter),
        pitcher=_player_summary(pitcher),
        plate_appearances=row.plate_appearances,
        at_bats=row.at_bats,
        hits=row.hits,
        doubles=row.doubles,
        triples=row.triples,
        home_runs=row.home_runs,
        walks=row.walks,
        hit_by_pitch=row.hit_by_pitch,
        strikeouts=row.strikeouts,
        rbi=row.rbi,
        avg=avg,
    )
