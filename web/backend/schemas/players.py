from typing import Optional

from pydantic import BaseModel


class PlayerSummary(BaseModel):
    id: int
    full_name: str
    boxscore_name: Optional[str]


class SeasonBattingStats(BaseModel):
    season: int
    team_id: Optional[int]
    games_played: int
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
    avg: Optional[float]
    obp: Optional[float]
    slg: Optional[float]
    ops: Optional[float]


class CareerBattingStats(BaseModel):
    games_played: int
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
    avg: Optional[float]
    obp: Optional[float]
    slg: Optional[float]
    ops: Optional[float]


class BattingStatsResponse(BaseModel):
    player: PlayerSummary
    seasons: list[SeasonBattingStats]
    postseason: list[SeasonBattingStats]
    career: Optional[CareerBattingStats]


class SeasonPitchingStats(BaseModel):
    season: int
    team_id: Optional[int]
    games_played: int
    games_started: int
    wins: int
    losses: int
    saves: int
    innings_pitched: str
    hits: int
    earned_runs: int
    base_on_balls: int
    strike_outs: int
    era: Optional[float]
    whip: Optional[float]
    k_per_9: Optional[float]
    bb_per_9: Optional[float]


class CareerPitchingStats(BaseModel):
    games_played: int
    games_started: int
    wins: int
    losses: int
    saves: int
    innings_pitched: str
    hits: int
    earned_runs: int
    base_on_balls: int
    strike_outs: int
    era: Optional[float]
    whip: Optional[float]
    k_per_9: Optional[float]
    bb_per_9: Optional[float]


class PitchingStatsResponse(BaseModel):
    player: PlayerSummary
    seasons: list[SeasonPitchingStats]
    postseason: list[SeasonPitchingStats]
    career: Optional[CareerPitchingStats]
