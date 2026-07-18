from datetime import date, datetime
from typing import Optional

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Numeric, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


def _nonneg_checks(table: str, *column_names: str) -> tuple[CheckConstraint, ...]:
    """CHECK (col >= 0) for every counting-stat column, so we don't hand-write 75 of these."""
    return tuple(
        CheckConstraint(f"{col} >= 0", name=f"ck_{table}_{col}_nonneg")
        for col in column_names
    )


class Game(Base):
    __tablename__ = "games"
    __table_args__ = (
        CheckConstraint("game_type IN ('R','F','D','L','W')", name="ck_games_game_type"),
        CheckConstraint("double_header IN ('Y','N','S')", name="ck_games_double_header"),
        CheckConstraint("home_score >= 0", name="ck_games_home_score_nonneg"),
        CheckConstraint("away_score >= 0", name="ck_games_away_score_nonneg"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    season: Mapped[int]
    game_type: Mapped[str] = mapped_column(String(2))
    game_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    official_date: Mapped[date] = mapped_column(Date)
    detailed_state: Mapped[str]
    day_night: Mapped[Optional[str]] = mapped_column(String(10))
    double_header: Mapped[str] = mapped_column(String(1), default="N")
    game_number: Mapped[int] = mapped_column(SmallInteger, default=1)
    venue_id: Mapped[int] = mapped_column(ForeignKey("venues.id", ondelete="RESTRICT"))
    home_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id", ondelete="RESTRICT"))
    away_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id", ondelete="RESTRICT"))
    home_score: Mapped[Optional[int]] = mapped_column(SmallInteger)
    away_score: Mapped[Optional[int]] = mapped_column(SmallInteger)
    is_tie: Mapped[bool] = mapped_column(default=False)
    scheduled_innings: Mapped[int] = mapped_column(SmallInteger)
    series_game_number: Mapped[Optional[int]] = mapped_column(SmallInteger)
    games_in_series: Mapped[Optional[int]] = mapped_column(SmallInteger)
    series_description: Mapped[Optional[str]]
    rescheduled_from: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))


class BattingBoxscore(Base):
    __tablename__ = "batting_boxscores"
    __table_args__ = _nonneg_checks(
        "batting_boxscores",
        "games_played", "fly_outs", "ground_outs", "air_outs", "runs", "doubles",
        "triples", "home_runs", "strike_outs", "base_on_balls", "intentional_walks",
        "hits", "hit_by_pitch", "at_bats", "caught_stealing", "stolen_bases",
        "ground_into_double_play", "ground_into_triple_play", "plate_appearances",
        "total_bases", "rbi", "left_on_base", "sac_bunts", "sac_flies",
        "catchers_interference", "pickoffs", "pop_outs", "line_outs",
    )

    game_id: Mapped[int] = mapped_column(ForeignKey("games.id", ondelete="CASCADE"), primary_key=True)
    player_id: Mapped[int] = mapped_column(
        ForeignKey("players.id", ondelete="RESTRICT"), primary_key=True, index=True
    )
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id", ondelete="RESTRICT"))

    position_code: Mapped[str] = mapped_column(String(2))
    position_name: Mapped[str]
    position_abbreviation: Mapped[str] = mapped_column(String(5))
    jersey_number: Mapped[Optional[str]] = mapped_column(String(3))

    games_played: Mapped[int] = mapped_column(SmallInteger, default=0)
    fly_outs: Mapped[int] = mapped_column(SmallInteger, default=0)
    ground_outs: Mapped[int] = mapped_column(SmallInteger, default=0)
    air_outs: Mapped[int] = mapped_column(SmallInteger, default=0)
    runs: Mapped[int] = mapped_column(SmallInteger, default=0)
    doubles: Mapped[int] = mapped_column(SmallInteger, default=0)
    triples: Mapped[int] = mapped_column(SmallInteger, default=0)
    home_runs: Mapped[int] = mapped_column(SmallInteger, default=0)
    strike_outs: Mapped[int] = mapped_column(SmallInteger, default=0)
    base_on_balls: Mapped[int] = mapped_column(SmallInteger, default=0)
    intentional_walks: Mapped[int] = mapped_column(SmallInteger, default=0)
    hits: Mapped[int] = mapped_column(SmallInteger, default=0)
    hit_by_pitch: Mapped[int] = mapped_column(SmallInteger, default=0)
    at_bats: Mapped[int] = mapped_column(SmallInteger, default=0)
    caught_stealing: Mapped[int] = mapped_column(SmallInteger, default=0)
    stolen_bases: Mapped[int] = mapped_column(SmallInteger, default=0)
    stolen_base_percentage: Mapped[Optional[float]] = mapped_column(Numeric(4, 3))
    ground_into_double_play: Mapped[int] = mapped_column(SmallInteger, default=0)
    ground_into_triple_play: Mapped[int] = mapped_column(SmallInteger, default=0)
    plate_appearances: Mapped[int] = mapped_column(SmallInteger, default=0)
    total_bases: Mapped[int] = mapped_column(SmallInteger, default=0)
    rbi: Mapped[int] = mapped_column(SmallInteger, default=0)
    left_on_base: Mapped[int] = mapped_column(SmallInteger, default=0)
    sac_bunts: Mapped[int] = mapped_column(SmallInteger, default=0)
    sac_flies: Mapped[int] = mapped_column(SmallInteger, default=0)
    catchers_interference: Mapped[int] = mapped_column(SmallInteger, default=0)
    pickoffs: Mapped[int] = mapped_column(SmallInteger, default=0)
    at_bats_per_home_run: Mapped[Optional[float]] = mapped_column(Numeric(6, 2))
    pop_outs: Mapped[int] = mapped_column(SmallInteger, default=0)
    line_outs: Mapped[int] = mapped_column(SmallInteger, default=0)
    summary: Mapped[Optional[str]]


class PitchingBoxscore(Base):
    __tablename__ = "pitching_boxscores"
    __table_args__ = _nonneg_checks(
        "pitching_boxscores",
        "games_played", "games_started", "fly_outs", "ground_outs", "air_outs",
        "runs", "doubles", "triples", "home_runs", "strike_outs", "base_on_balls",
        "intentional_walks", "hits", "hit_by_pitch", "at_bats", "caught_stealing",
        "stolen_bases", "number_of_pitches", "outs", "wins", "losses", "saves",
        "save_opportunities", "holds", "blown_saves", "earned_runs", "batters_faced",
        "games_pitched", "complete_games", "shutouts", "pitches_thrown", "balls",
        "strikes", "hit_batsmen", "balks", "wild_pitches", "pickoffs", "rbi",
        "games_finished", "inherited_runners", "inherited_runners_scored",
        "catchers_interference", "sac_bunts", "sac_flies", "passed_ball",
        "pop_outs", "line_outs",
    )

    game_id: Mapped[int] = mapped_column(ForeignKey("games.id", ondelete="CASCADE"), primary_key=True)
    player_id: Mapped[int] = mapped_column(
        ForeignKey("players.id", ondelete="RESTRICT"), primary_key=True, index=True
    )
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id", ondelete="RESTRICT"))

    position_code: Mapped[str] = mapped_column(String(2))
    position_name: Mapped[str]
    position_abbreviation: Mapped[str] = mapped_column(String(5))
    jersey_number: Mapped[Optional[str]] = mapped_column(String(3))

    note: Mapped[Optional[str]]
    summary: Mapped[Optional[str]]
    games_played: Mapped[int] = mapped_column(SmallInteger, default=0)
    games_started: Mapped[int] = mapped_column(SmallInteger, default=0)
    fly_outs: Mapped[int] = mapped_column(SmallInteger, default=0)
    ground_outs: Mapped[int] = mapped_column(SmallInteger, default=0)
    air_outs: Mapped[int] = mapped_column(SmallInteger, default=0)
    runs: Mapped[int] = mapped_column(SmallInteger, default=0)
    doubles: Mapped[int] = mapped_column(SmallInteger, default=0)
    triples: Mapped[int] = mapped_column(SmallInteger, default=0)
    home_runs: Mapped[int] = mapped_column(SmallInteger, default=0)
    strike_outs: Mapped[int] = mapped_column(SmallInteger, default=0)
    base_on_balls: Mapped[int] = mapped_column(SmallInteger, default=0)
    intentional_walks: Mapped[int] = mapped_column(SmallInteger, default=0)
    hits: Mapped[int] = mapped_column(SmallInteger, default=0)
    hit_by_pitch: Mapped[int] = mapped_column(SmallInteger, default=0)
    at_bats: Mapped[int] = mapped_column(SmallInteger, default=0)
    caught_stealing: Mapped[int] = mapped_column(SmallInteger, default=0)
    stolen_bases: Mapped[int] = mapped_column(SmallInteger, default=0)
    stolen_base_percentage: Mapped[Optional[float]] = mapped_column(Numeric(4, 3))
    number_of_pitches: Mapped[int] = mapped_column(SmallInteger, default=0)
    innings_pitched: Mapped[str] = mapped_column(String(5), default="0.0")
    outs: Mapped[int] = mapped_column(SmallInteger, default=0)
    wins: Mapped[int] = mapped_column(SmallInteger, default=0)
    losses: Mapped[int] = mapped_column(SmallInteger, default=0)
    saves: Mapped[int] = mapped_column(SmallInteger, default=0)
    save_opportunities: Mapped[int] = mapped_column(SmallInteger, default=0)
    holds: Mapped[int] = mapped_column(SmallInteger, default=0)
    blown_saves: Mapped[int] = mapped_column(SmallInteger, default=0)
    earned_runs: Mapped[int] = mapped_column(SmallInteger, default=0)
    batters_faced: Mapped[int] = mapped_column(SmallInteger, default=0)
    games_pitched: Mapped[int] = mapped_column(SmallInteger, default=0)
    complete_games: Mapped[int] = mapped_column(SmallInteger, default=0)
    shutouts: Mapped[int] = mapped_column(SmallInteger, default=0)
    pitches_thrown: Mapped[int] = mapped_column(SmallInteger, default=0)
    balls: Mapped[int] = mapped_column(SmallInteger, default=0)
    strikes: Mapped[int] = mapped_column(SmallInteger, default=0)
    strike_percentage: Mapped[Optional[float]] = mapped_column(Numeric(4, 3))
    hit_batsmen: Mapped[int] = mapped_column(SmallInteger, default=0)
    balks: Mapped[int] = mapped_column(SmallInteger, default=0)
    wild_pitches: Mapped[int] = mapped_column(SmallInteger, default=0)
    pickoffs: Mapped[int] = mapped_column(SmallInteger, default=0)
    rbi: Mapped[int] = mapped_column(SmallInteger, default=0)
    games_finished: Mapped[int] = mapped_column(SmallInteger, default=0)
    runs_scored_per9: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    home_runs_per9: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    inherited_runners: Mapped[int] = mapped_column(SmallInteger, default=0)
    inherited_runners_scored: Mapped[int] = mapped_column(SmallInteger, default=0)
    catchers_interference: Mapped[int] = mapped_column(SmallInteger, default=0)
    sac_bunts: Mapped[int] = mapped_column(SmallInteger, default=0)
    sac_flies: Mapped[int] = mapped_column(SmallInteger, default=0)
    passed_ball: Mapped[int] = mapped_column(SmallInteger, default=0)
    pop_outs: Mapped[int] = mapped_column(SmallInteger, default=0)
    line_outs: Mapped[int] = mapped_column(SmallInteger, default=0)
