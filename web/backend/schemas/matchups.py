from typing import Optional

from pydantic import BaseModel

from schemas.players import PlayerSummary


class MatchupStats(BaseModel):
    batter: PlayerSummary
    pitcher: PlayerSummary
    plate_appearances: int
    at_bats: int
    hits: int
    doubles: int
    triples: int
    home_runs: int
    walks: int
    hit_by_pitch: int
    strikeouts: int
    rbi: int
    avg: Optional[float]
