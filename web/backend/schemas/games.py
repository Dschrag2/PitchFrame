from datetime import date
from typing import Optional

from pydantic import BaseModel


class TeamSummary(BaseModel):
    id: int
    name: str
    abbreviation: str


class GameSummary(BaseModel):
    id: int
    season: int
    game_type: str
    official_date: date
    detailed_state: str
    home_team: TeamSummary
    away_team: TeamSummary
    home_score: Optional[int]
    away_score: Optional[int]


class BattingLine(BaseModel):
    player_id: int
    player_name: str
    position: str
    at_bats: int
    runs: int
    hits: int
    doubles: int
    triples: int
    home_runs: int
    rbi: int
    base_on_balls: int
    strike_outs: int
    stolen_bases: int
    summary: Optional[str]


class PitchingLine(BaseModel):
    player_id: int
    player_name: str
    innings_pitched: str
    hits: int
    runs: int
    earned_runs: int
    base_on_balls: int
    strike_outs: int
    home_runs: int
    summary: Optional[str]


class TeamBoxscore(BaseModel):
    team: TeamSummary
    batting: list[BattingLine]
    pitching: list[PitchingLine]


class GameBoxscore(BaseModel):
    game: GameSummary
    home: TeamBoxscore
    away: TeamBoxscore
