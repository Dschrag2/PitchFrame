from typing import Optional

from pydantic import BaseModel

from schemas.players import PlayerSummary
from schemas.teams import TeamDetail


class RosterBatter(BaseModel):
    player: PlayerSummary
    games_played: int
    at_bats: int
    hits: int
    home_runs: int
    rbi: int
    avg: Optional[float]
    ops: Optional[float]


class RosterPitcher(BaseModel):
    player: PlayerSummary
    games_played: int
    games_started: int
    wins: int
    losses: int
    saves: int
    strike_outs: int
    era: Optional[float]
    whip: Optional[float]


class TeamRoster(BaseModel):
    team: TeamDetail
    season: int
    batters: list[RosterBatter]
    pitchers: list[RosterPitcher]
