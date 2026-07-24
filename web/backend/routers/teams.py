from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models import Player, Team
from db.stats_views import player_season_batting_stats, player_season_pitching_stats

from dependencies import get_db
from schemas.players import PlayerSummary
from schemas.roster import RosterBatter, RosterPitcher, TeamRoster
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


def _get_team_or_404(db: Session, team_id: int) -> Team:
    team = db.get(Team, team_id)
    if team is None:
        raise HTTPException(status_code=404, detail=f"Team {team_id} not found")
    return team


@router.get("/{team_id}", response_model=TeamDetail)
def get_team(team_id: int, db: Session = Depends(get_db)):
    return _team_detail(_get_team_or_404(db, team_id))


@router.get("/{team_id}/roster", response_model=TeamRoster)
def get_team_roster(team_id: int, season: int = Query(...), db: Session = Depends(get_db)):
    team = _get_team_or_404(db, team_id)

    def _player_summary(player_id: int, players: dict[int, Player]) -> PlayerSummary:
        p = players[player_id]
        return PlayerSummary(id=p.id, full_name=p.full_name, boxscore_name=p.boxscore_name)

    batting_rows = db.execute(
        select(player_season_batting_stats).where(
            player_season_batting_stats.c.team_id == team_id,
            player_season_batting_stats.c.season == season,
        )
    ).all()
    pitching_rows = db.execute(
        select(player_season_pitching_stats).where(
            player_season_pitching_stats.c.team_id == team_id,
            player_season_pitching_stats.c.season == season,
        )
    ).all()

    player_ids = {r.player_id for r in batting_rows} | {r.player_id for r in pitching_rows}
    players = {p.id: p for p in db.execute(select(Player).where(Player.id.in_(player_ids))).scalars()}

    batters = sorted(
        [
            RosterBatter(
                player=_player_summary(r.player_id, players),
                games_played=r.games_played,
                at_bats=r.at_bats,
                hits=r.hits,
                home_runs=r.home_runs,
                rbi=r.rbi,
                avg=r.avg,
                ops=r.ops,
            )
            for r in batting_rows
        ],
        key=lambda b: b.at_bats,
        reverse=True,
    )
    pitchers = sorted(
        [
            RosterPitcher(
                player=_player_summary(r.player_id, players),
                games_played=r.games_played,
                games_started=r.games_started,
                wins=r.wins,
                losses=r.losses,
                saves=r.saves,
                strike_outs=r.strike_outs,
                era=r.era,
                whip=r.whip,
            )
            for r in pitching_rows
        ],
        key=lambda p: p.games_played,
        reverse=True,
    )

    return TeamRoster(team=_team_detail(team), season=season, batters=batters, pitchers=pitchers)
