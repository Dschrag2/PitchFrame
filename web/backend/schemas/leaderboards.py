from typing import Optional

from pydantic import BaseModel

from schemas.players import PlayerSummary


class LeaderboardEntry(BaseModel):
    rank: int
    player: PlayerSummary
    value: float
    games_played: int
