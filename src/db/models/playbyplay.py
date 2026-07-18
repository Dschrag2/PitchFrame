import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Numeric,
    SmallInteger,
    String,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class AtBat(Base):
    __tablename__ = "at_bats"
    __table_args__ = (
        CheckConstraint("bases BETWEEN 0 AND 4", name="ck_at_bats_bases_range"),
        Index("ix_at_bats_batter_pitcher", "batter_id", "pitcher_id"),
        Index("ix_at_bats_pitcher_batter", "pitcher_id", "batter_id"),
    )

    game_id: Mapped[int] = mapped_column(ForeignKey("games.id", ondelete="CASCADE"), primary_key=True)
    at_bat_index: Mapped[int] = mapped_column(SmallInteger, primary_key=True)

    inning: Mapped[int] = mapped_column(SmallInteger)
    half_inning: Mapped[str] = mapped_column(String(3))
    batter_id: Mapped[int] = mapped_column(ForeignKey("players.id", ondelete="RESTRICT"))
    pitcher_id: Mapped[int] = mapped_column(ForeignKey("players.id", ondelete="RESTRICT"))
    bat_side: Mapped[str] = mapped_column(String(1))
    pitch_hand: Mapped[str] = mapped_column(String(1))
    event: Mapped[str]
    event_type: Mapped[str]
    description: Mapped[str]
    rbi: Mapped[int] = mapped_column(SmallInteger, default=0)
    is_scoring_play: Mapped[bool] = mapped_column(default=False)
    is_out: Mapped[bool] = mapped_column(default=False)
    home_score: Mapped[int] = mapped_column(SmallInteger)
    away_score: Mapped[int] = mapped_column(SmallInteger)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    is_at_bat: Mapped[bool] = mapped_column(default=False)
    is_hit: Mapped[bool] = mapped_column(default=False)
    is_walk: Mapped[bool] = mapped_column(default=False)
    is_hit_by_pitch: Mapped[bool] = mapped_column(default=False)
    is_strikeout: Mapped[bool] = mapped_column(default=False)
    is_sac_fly: Mapped[bool] = mapped_column(default=False)
    is_sac_bunt: Mapped[bool] = mapped_column(default=False)
    bases: Mapped[int] = mapped_column(SmallInteger, default=0)


class Event(Base):
    __tablename__ = "events"
    __table_args__ = (
        ForeignKeyConstraint(
            ["game_id", "at_bat_index"],
            ["at_bats.game_id", "at_bats.at_bat_index"],
            ondelete="CASCADE",
        ),
        UniqueConstraint("game_id", "global_sequence"),
    )

    game_id: Mapped[int] = mapped_column(primary_key=True)
    at_bat_index: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    event_index: Mapped[int] = mapped_column(SmallInteger, primary_key=True)

    global_sequence: Mapped[int]
    event_type: Mapped[str] = mapped_column(String(10))
    is_pitch: Mapped[bool]
    event_code: Mapped[str]
    event_name: Mapped[str]
    description: Mapped[str]
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    home_score: Mapped[int] = mapped_column(SmallInteger)
    away_score: Mapped[int] = mapped_column(SmallInteger)
    related_player_id: Mapped[Optional[int]] = mapped_column(ForeignKey("players.id", ondelete="RESTRICT"))


class Pitch(Base):
    __tablename__ = "pitches"
    __table_args__ = (
        ForeignKeyConstraint(
            ["game_id", "at_bat_index", "event_index"],
            ["events.game_id", "events.at_bat_index", "events.event_index"],
            ondelete="CASCADE",
        ),
        CheckConstraint("balls BETWEEN 0 AND 3", name="ck_pitches_balls_range"),
        CheckConstraint("strikes BETWEEN 0 AND 2", name="ck_pitches_strikes_range"),
        CheckConstraint("outs BETWEEN 0 AND 2", name="ck_pitches_outs_range"),
        Index("ix_pitches_batter_pitcher", "batter_id", "pitcher_id"),
        Index("ix_pitches_pitcher_batter", "pitcher_id", "batter_id"),
        UniqueConstraint("play_id"),
    )

    game_id: Mapped[int] = mapped_column(primary_key=True)
    at_bat_index: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    event_index: Mapped[int] = mapped_column(SmallInteger, primary_key=True)

    batter_id: Mapped[int] = mapped_column(ForeignKey("players.id", ondelete="RESTRICT"))
    pitcher_id: Mapped[int] = mapped_column(ForeignKey("players.id", ondelete="RESTRICT"))

    pitch_number: Mapped[int] = mapped_column(SmallInteger)
    balls: Mapped[int] = mapped_column(SmallInteger)
    strikes: Mapped[int] = mapped_column(SmallInteger)
    outs: Mapped[int] = mapped_column(SmallInteger)
    pitch_type_code: Mapped[Optional[str]] = mapped_column(String(3))
    pitch_type_description: Mapped[Optional[str]]
    call_code: Mapped[str] = mapped_column(String(3))
    call_description: Mapped[str]
    is_strike: Mapped[bool]
    is_ball: Mapped[bool]
    is_in_play: Mapped[bool]

    start_speed: Mapped[Optional[float]] = mapped_column(Numeric(4, 1))
    end_speed: Mapped[Optional[float]] = mapped_column(Numeric(4, 1))
    spin_rate: Mapped[Optional[int]]
    spin_direction: Mapped[Optional[int]]
    break_angle: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    break_length: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    break_vertical: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    break_vertical_induced: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    break_horizontal: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    zone: Mapped[Optional[int]] = mapped_column(SmallInteger)
    type_confidence: Mapped[Optional[float]] = mapped_column(Numeric(4, 3))
    plate_time: Mapped[Optional[float]] = mapped_column(Numeric(6, 4))
    extension: Mapped[Optional[float]] = mapped_column(Numeric(5, 3))
    strike_zone_top: Mapped[Optional[float]] = mapped_column(Numeric(4, 2))
    strike_zone_bottom: Mapped[Optional[float]] = mapped_column(Numeric(4, 2))
    plate_x: Mapped[Optional[float]] = mapped_column(Numeric(6, 4))
    plate_z: Mapped[Optional[float]] = mapped_column(Numeric(6, 4))
    release_pos_x: Mapped[Optional[float]] = mapped_column(Numeric(6, 4))
    release_pos_y: Mapped[Optional[float]] = mapped_column(Numeric(6, 4))
    release_pos_z: Mapped[Optional[float]] = mapped_column(Numeric(6, 4))
    vx0: Mapped[Optional[float]] = mapped_column(Numeric(8, 4))
    vy0: Mapped[Optional[float]] = mapped_column(Numeric(8, 4))
    vz0: Mapped[Optional[float]] = mapped_column(Numeric(8, 4))
    ax: Mapped[Optional[float]] = mapped_column(Numeric(8, 4))
    ay: Mapped[Optional[float]] = mapped_column(Numeric(8, 4))
    az: Mapped[Optional[float]] = mapped_column(Numeric(8, 4))
    pfx_x: Mapped[Optional[float]] = mapped_column(Numeric(6, 3))
    pfx_z: Mapped[Optional[float]] = mapped_column(Numeric(6, 3))
    play_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)


class BattedBall(Base):
    __tablename__ = "batted_balls"
    __table_args__ = (
        ForeignKeyConstraint(
            ["game_id", "at_bat_index", "event_index"],
            ["pitches.game_id", "pitches.at_bat_index", "pitches.event_index"],
            ondelete="CASCADE",
        ),
    )

    game_id: Mapped[int] = mapped_column(primary_key=True)
    at_bat_index: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    event_index: Mapped[int] = mapped_column(SmallInteger, primary_key=True)

    launch_speed: Mapped[Optional[float]] = mapped_column(Numeric(4, 1))
    launch_angle: Mapped[Optional[float]] = mapped_column(Numeric(5, 1))
    total_distance: Mapped[Optional[float]] = mapped_column(Numeric(6, 1))
    trajectory: Mapped[Optional[str]]
    hardness: Mapped[Optional[str]]
    location: Mapped[Optional[str]] = mapped_column(String(2))
    coord_x: Mapped[Optional[float]] = mapped_column(Numeric(7, 2))
    coord_y: Mapped[Optional[float]] = mapped_column(Numeric(7, 2))


class BaserunningEvent(Base):
    __tablename__ = "baserunning_events"
    __table_args__ = (
        ForeignKeyConstraint(
            ["game_id", "at_bat_index", "event_index"],
            ["events.game_id", "events.at_bat_index", "events.event_index"],
            ondelete="CASCADE",
        ),
    )

    game_id: Mapped[int] = mapped_column(primary_key=True)
    at_bat_index: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    event_index: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    runner_id: Mapped[int] = mapped_column(
        ForeignKey("players.id", ondelete="RESTRICT"), primary_key=True
    )

    origin_base: Mapped[Optional[str]] = mapped_column(String(2))
    start_base: Mapped[Optional[str]] = mapped_column(String(2))
    end_base: Mapped[Optional[str]] = mapped_column(String(2))
    out_base: Mapped[Optional[str]] = mapped_column(String(2))
    is_out: Mapped[bool] = mapped_column(default=False)
    out_number: Mapped[Optional[int]] = mapped_column(SmallInteger)
    movement_reason: Mapped[Optional[str]]
    responsible_pitcher_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("players.id", ondelete="RESTRICT")
    )
    is_scoring_event: Mapped[bool] = mapped_column(default=False)
    rbi: Mapped[bool] = mapped_column(default=False)
    earned: Mapped[bool] = mapped_column(default=False)
    team_unearned: Mapped[bool] = mapped_column(default=False)


class BaserunningEventCredit(Base):
    __tablename__ = "baserunning_event_credits"
    __table_args__ = (
        ForeignKeyConstraint(
            ["game_id", "at_bat_index", "event_index", "runner_id"],
            [
                "baserunning_events.game_id",
                "baserunning_events.at_bat_index",
                "baserunning_events.event_index",
                "baserunning_events.runner_id",
            ],
            ondelete="CASCADE",
        ),
    )

    game_id: Mapped[int] = mapped_column(primary_key=True)
    at_bat_index: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    event_index: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    runner_id: Mapped[int] = mapped_column(primary_key=True)
    credit_index: Mapped[int] = mapped_column(SmallInteger, primary_key=True)

    player_id: Mapped[int] = mapped_column(ForeignKey("players.id", ondelete="RESTRICT"))
    position_code: Mapped[str] = mapped_column(String(2))
    position_name: Mapped[str]
    position_abbreviation: Mapped[str] = mapped_column(String(5))
    credit_type: Mapped[str]
