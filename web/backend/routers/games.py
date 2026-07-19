from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, aliased

from db.models import BattingBoxscore, Game, PitchingBoxscore, Player, Team

from dependencies import get_db
from schemas.games import BattingLine, GameBoxscore, GameSummary, PitchingLine, TeamBoxscore, TeamSummary

router = APIRouter(prefix="/games", tags=["games"])


def _team_summary(team: Team) -> TeamSummary:
    return TeamSummary(id=team.id, name=team.name, abbreviation=team.abbreviation)


def _fetch_game_with_teams(db: Session, game_id: int):
    HomeTeam = aliased(Team)
    AwayTeam = aliased(Team)
    stmt = (
        select(Game, HomeTeam, AwayTeam)
        .join(HomeTeam, HomeTeam.id == Game.home_team_id)
        .join(AwayTeam, AwayTeam.id == Game.away_team_id)
        .where(Game.id == game_id)
    )
    row = db.execute(stmt).first()
    if row is None:
        raise HTTPException(status_code=404, detail=f"Game {game_id} not found")
    return row


@router.get("", response_model=list[GameSummary])
def list_games(
    season: Optional[int] = Query(None),
    team_id: Optional[int] = Query(None),
    limit: int = Query(50, le=200),
    offset: int = Query(0),
    db: Session = Depends(get_db),
):
    HomeTeam = aliased(Team)
    AwayTeam = aliased(Team)

    stmt = (
        select(Game, HomeTeam, AwayTeam)
        .join(HomeTeam, HomeTeam.id == Game.home_team_id)
        .join(AwayTeam, AwayTeam.id == Game.away_team_id)
        .order_by(Game.official_date, Game.id)
        .limit(limit)
        .offset(offset)
    )
    if season is not None:
        stmt = stmt.where(Game.season == season)
    if team_id is not None:
        stmt = stmt.where((Game.home_team_id == team_id) | (Game.away_team_id == team_id))

    rows = db.execute(stmt).all()
    return [
        GameSummary(
            id=game.id,
            season=game.season,
            game_type=game.game_type,
            official_date=game.official_date,
            detailed_state=game.detailed_state,
            home_team=_team_summary(home),
            away_team=_team_summary(away),
            home_score=game.home_score,
            away_score=game.away_score,
        )
        for game, home, away in rows
    ]


def _game_summary(game: Game, home: Team, away: Team) -> GameSummary:
    return GameSummary(
        id=game.id,
        season=game.season,
        game_type=game.game_type,
        official_date=game.official_date,
        detailed_state=game.detailed_state,
        home_team=_team_summary(home),
        away_team=_team_summary(away),
        home_score=game.home_score,
        away_score=game.away_score,
    )


@router.get("/{game_id}", response_model=GameSummary)
def get_game(game_id: int, db: Session = Depends(get_db)):
    game, home, away = _fetch_game_with_teams(db, game_id)
    return _game_summary(game, home, away)


def _batting_lines(db: Session, game_id: int, team_id: int) -> list[BattingLine]:
    stmt = (
        select(BattingBoxscore, Player)
        .join(Player, Player.id == BattingBoxscore.player_id)
        .where(BattingBoxscore.game_id == game_id, BattingBoxscore.team_id == team_id)
        .order_by(BattingBoxscore.at_bats.desc())
    )
    rows = db.execute(stmt).all()
    return [
        BattingLine(
            player_id=player.id,
            player_name=player.full_name,
            position=b.position_abbreviation,
            at_bats=b.at_bats,
            runs=b.runs,
            hits=b.hits,
            doubles=b.doubles,
            triples=b.triples,
            home_runs=b.home_runs,
            rbi=b.rbi,
            base_on_balls=b.base_on_balls,
            strike_outs=b.strike_outs,
            stolen_bases=b.stolen_bases,
            summary=b.summary,
        )
        for b, player in rows
    ]


def _pitching_lines(db: Session, game_id: int, team_id: int) -> list[PitchingLine]:
    stmt = (
        select(PitchingBoxscore, Player)
        .join(Player, Player.id == PitchingBoxscore.player_id)
        .where(PitchingBoxscore.game_id == game_id, PitchingBoxscore.team_id == team_id)
        .order_by(PitchingBoxscore.outs.desc())
    )
    rows = db.execute(stmt).all()
    return [
        PitchingLine(
            player_id=player.id,
            player_name=player.full_name,
            innings_pitched=p.innings_pitched,
            hits=p.hits,
            runs=p.runs,
            earned_runs=p.earned_runs,
            base_on_balls=p.base_on_balls,
            strike_outs=p.strike_outs,
            home_runs=p.home_runs,
            summary=p.summary,
        )
        for p, player in rows
    ]


@router.get("/{game_id}/boxscore", response_model=GameBoxscore)
def get_boxscore(game_id: int, db: Session = Depends(get_db)):
    game, home, away = _fetch_game_with_teams(db, game_id)

    return GameBoxscore(
        game=_game_summary(game, home, away),
        home=TeamBoxscore(
            team=_team_summary(home),
            batting=_batting_lines(db, game_id, home.id),
            pitching=_pitching_lines(db, game_id, home.id),
        ),
        away=TeamBoxscore(
            team=_team_summary(away),
            batting=_batting_lines(db, game_id, away.id),
            pitching=_pitching_lines(db, game_id, away.id),
        ),
    )
