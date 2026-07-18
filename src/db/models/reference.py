from typing import Optional

from sqlalchemy import Numeric, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class Venue(Base):
    __tablename__ = "venues"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    name: Mapped[str]
    city: Mapped[Optional[str]]
    state: Mapped[Optional[str]]
    postal_code: Mapped[Optional[str]]
    latitude: Mapped[Optional[float]] = mapped_column(Numeric)
    longitude: Mapped[Optional[float]] = mapped_column(Numeric)
    azimuth_angle: Mapped[Optional[float]] = mapped_column(Numeric)
    elevation: Mapped[Optional[int]]
    time_zone: Mapped[Optional[str]]
    capacity: Mapped[Optional[int]]
    turf_type: Mapped[Optional[str]]
    roof_type: Mapped[Optional[str]]
    left_line: Mapped[Optional[int]] = mapped_column(SmallInteger)
    left_center: Mapped[Optional[int]] = mapped_column(SmallInteger)
    center: Mapped[Optional[int]] = mapped_column(SmallInteger)
    right_center: Mapped[Optional[int]] = mapped_column(SmallInteger)
    right_line: Mapped[Optional[int]] = mapped_column(SmallInteger)


class Team(Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    name: Mapped[str]
    team_name: Mapped[Optional[str]]
    location_name: Mapped[Optional[str]]
    abbreviation: Mapped[str] = mapped_column(String(5))
    team_code: Mapped[Optional[str]] = mapped_column(String(10))
    league_id: Mapped[Optional[int]]
    league_name: Mapped[Optional[str]]
    division_id: Mapped[Optional[int]]
    division_name: Mapped[Optional[str]]
    first_year_of_play: Mapped[Optional[str]] = mapped_column(String(4))
    active: Mapped[bool] = mapped_column(default=True)


class Player(Base):
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    full_name: Mapped[str]
    boxscore_name: Mapped[Optional[str]]
