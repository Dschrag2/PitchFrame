from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models import Team

from dependencies import get_db
from schemas.teams import TeamDetail

router = APIRouter(prefix="/teams", tags=["teams"])


def _team_detail(team: Team) -> TeamDetail:
    return TeamDetail(
        id=team.id,
        name=team.name,
        team_name=team.team_name,
        location_name=team.location_name,
        abbreviation=team.abbreviation,
        league_name=team.league_name,
        division_name=team.division_name,
        first_year_of_play=team.first_year_of_play,
        active=team.active,
    )


@router.get("", response_model=list[TeamDetail])
def list_teams(db: Session = Depends(get_db)):
    teams = db.execute(select(Team).order_by(Team.name)).scalars().all()
    return [_team_detail(t) for t in teams]


@router.get("/{team_id}", response_model=TeamDetail)
def get_team(team_id: int, db: Session = Depends(get_db)):
    team = db.get(Team, team_id)
    if team is None:
        raise HTTPException(status_code=404, detail=f"Team {team_id} not found")
    return _team_detail(team)
