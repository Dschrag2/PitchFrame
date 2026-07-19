from typing import Optional

from pydantic import BaseModel


class TeamDetail(BaseModel):
    id: int
    name: str
    team_name: str
    location_name: Optional[str]
    abbreviation: str
    league_name: Optional[str]
    division_name: Optional[str]
    first_year_of_play: Optional[str]
    active: bool
