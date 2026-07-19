"""
stats_views.py

Core Table objects reflecting the season/postseason/career stat materialized
views (created via raw SQL in Alembic migrations, not declarative models).
Columns are read directly from Postgres at import time rather than
hand-declared, since the view's own SQL is the single source of truth for
its columns. These live in their own MetaData object, separate from
Base.metadata, so Alembic's autogenerate never sees or tries to manage them.
"""

from sqlalchemy import MetaData, Table

from db.base import engine

_metadata = MetaData()

player_season_batting_stats = Table("player_season_batting_stats", _metadata, autoload_with=engine)
player_season_pitching_stats = Table("player_season_pitching_stats", _metadata, autoload_with=engine)
player_postseason_batting_stats = Table("player_postseason_batting_stats", _metadata, autoload_with=engine)
player_postseason_pitching_stats = Table("player_postseason_pitching_stats", _metadata, autoload_with=engine)
player_career_batting_stats = Table("player_career_batting_stats", _metadata, autoload_with=engine)
player_career_pitching_stats = Table("player_career_pitching_stats", _metadata, autoload_with=engine)
