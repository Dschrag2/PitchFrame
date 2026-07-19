"""split season stats to regular season only and add postseason views

Revision ID: 63cc57239a55
Revises: 5a27af8c48af
Create Date: 2026-07-19 14:05:46.587829

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '63cc57239a55'
down_revision: Union[str, Sequence[str], None] = '5a27af8c48af'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


BATTING_SUM_COLS = [
    "games_played", "fly_outs", "ground_outs", "air_outs", "runs", "doubles", "triples",
    "home_runs", "strike_outs", "base_on_balls", "intentional_walks", "hits", "hit_by_pitch",
    "at_bats", "caught_stealing", "stolen_bases", "ground_into_double_play",
    "ground_into_triple_play", "plate_appearances", "total_bases", "rbi", "left_on_base",
    "sac_bunts", "sac_flies", "catchers_interference", "pickoffs", "pop_outs", "line_outs",
]

PITCHING_SUM_COLS = [
    "games_played", "games_started", "fly_outs", "ground_outs", "air_outs", "runs", "doubles",
    "triples", "home_runs", "strike_outs", "base_on_balls", "intentional_walks", "hits",
    "hit_by_pitch", "at_bats", "caught_stealing", "stolen_bases", "number_of_pitches", "outs",
    "wins", "losses", "saves", "save_opportunities", "holds", "blown_saves", "earned_runs",
    "batters_faced", "games_pitched", "complete_games", "shutouts", "pitches_thrown", "balls",
    "strikes", "hit_batsmen", "balks", "wild_pitches", "pickoffs", "rbi", "games_finished",
    "inherited_runners", "inherited_runners_scored", "catchers_interference", "sac_bunts",
    "sac_flies", "passed_ball", "pop_outs", "line_outs",
]


def _sum_lines(cols: list[str], alias: str) -> str:
    return ",\n    ".join(f"SUM({alias}.{c}) AS {c}" for c in cols)


BATTING_RATE_STATS = """
    ROUND(SUM(b.hits)::numeric / NULLIF(SUM(b.at_bats), 0), 3) AS avg,
    ROUND((SUM(b.hits) + SUM(b.base_on_balls) + SUM(b.hit_by_pitch))::numeric
        / NULLIF(SUM(b.at_bats) + SUM(b.base_on_balls) + SUM(b.hit_by_pitch) + SUM(b.sac_flies), 0), 3) AS obp,
    ROUND(SUM(b.total_bases)::numeric / NULLIF(SUM(b.at_bats), 0), 3) AS slg,
    ROUND(
        (SUM(b.hits) + SUM(b.base_on_balls) + SUM(b.hit_by_pitch))::numeric
            / NULLIF(SUM(b.at_bats) + SUM(b.base_on_balls) + SUM(b.hit_by_pitch) + SUM(b.sac_flies), 0)
        + SUM(b.total_bases)::numeric / NULLIF(SUM(b.at_bats), 0)
    , 3) AS ops"""

PITCHING_RATE_STATS = """
    ROUND(9.0 * SUM(p.earned_runs) / NULLIF(SUM(p.outs) / 3.0, 0), 2) AS era,
    ROUND((SUM(p.base_on_balls) + SUM(p.hits))::numeric / NULLIF(SUM(p.outs) / 3.0, 0), 3) AS whip,
    ROUND(9.0 * SUM(p.strike_outs) / NULLIF(SUM(p.outs) / 3.0, 0), 2) AS k_per_9,
    ROUND(9.0 * SUM(p.base_on_balls) / NULLIF(SUM(p.outs) / 3.0, 0), 2) AS bb_per_9"""

POSTSEASON_GAME_TYPES = "('F','D','L','W')"


def _period_view(name: str, side: str, sum_cols: list[str], rate_stats: str, game_type_filter: str) -> str:
    alias = "b" if side == "batting" else "p"
    table = "batting_boxscores" if side == "batting" else "pitching_boxscores"
    sums = _sum_lines(sum_cols, alias)
    return f"""
        CREATE MATERIALIZED VIEW {name} AS
        SELECT
            {alias}.player_id,
            g.season,
            {alias}.team_id,
            {sums},
            {rate_stats.strip()}
        FROM {table} {alias}
        JOIN games g ON g.id = {alias}.game_id
        WHERE {game_type_filter}
        GROUP BY {alias}.player_id, g.season, {alias}.team_id

        UNION ALL

        SELECT
            {alias}.player_id,
            g.season,
            NULL::integer AS team_id,
            {sums},
            {rate_stats.strip()}
        FROM {table} {alias}
        JOIN games g ON g.id = {alias}.game_id
        WHERE {game_type_filter}
        GROUP BY {alias}.player_id, g.season
        HAVING COUNT(DISTINCT {alias}.team_id) > 1;
    """


def upgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_player_season_batting_stats_pk;")
    op.execute("DROP INDEX IF EXISTS ix_player_season_pitching_stats_pk;")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS player_season_batting_stats;")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS player_season_pitching_stats;")

    op.execute(_period_view(
        "player_season_batting_stats", "batting", BATTING_SUM_COLS, BATTING_RATE_STATS, "g.game_type = 'R'"
    ))
    op.execute("""
        CREATE UNIQUE INDEX ix_player_season_batting_stats_pk
            ON player_season_batting_stats (player_id, season, team_id)
            NULLS NOT DISTINCT;
    """)

    op.execute(_period_view(
        "player_season_pitching_stats", "pitching", PITCHING_SUM_COLS, PITCHING_RATE_STATS, "g.game_type = 'R'"
    ))
    op.execute("""
        CREATE UNIQUE INDEX ix_player_season_pitching_stats_pk
            ON player_season_pitching_stats (player_id, season, team_id)
            NULLS NOT DISTINCT;
    """)

    op.execute(_period_view(
        "player_postseason_batting_stats", "batting", BATTING_SUM_COLS, BATTING_RATE_STATS,
        f"g.game_type IN {POSTSEASON_GAME_TYPES}",
    ))
    op.execute("""
        CREATE UNIQUE INDEX ix_player_postseason_batting_stats_pk
            ON player_postseason_batting_stats (player_id, season, team_id)
            NULLS NOT DISTINCT;
    """)

    op.execute(_period_view(
        "player_postseason_pitching_stats", "pitching", PITCHING_SUM_COLS, PITCHING_RATE_STATS,
        f"g.game_type IN {POSTSEASON_GAME_TYPES}",
    ))
    op.execute("""
        CREATE UNIQUE INDEX ix_player_postseason_pitching_stats_pk
            ON player_postseason_pitching_stats (player_id, season, team_id)
            NULLS NOT DISTINCT;
    """)


def downgrade() -> None:
    op.execute("DROP MATERIALIZED VIEW IF EXISTS player_postseason_pitching_stats;")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS player_postseason_batting_stats;")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS player_season_pitching_stats;")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS player_season_batting_stats;")

    op.execute(_period_view(
        "player_season_batting_stats", "batting", BATTING_SUM_COLS, BATTING_RATE_STATS, "TRUE"
    ))
    op.execute("""
        CREATE UNIQUE INDEX ix_player_season_batting_stats_pk
            ON player_season_batting_stats (player_id, season, team_id)
            NULLS NOT DISTINCT;
    """)
    op.execute(_period_view(
        "player_season_pitching_stats", "pitching", PITCHING_SUM_COLS, PITCHING_RATE_STATS, "TRUE"
    ))
    op.execute("""
        CREATE UNIQUE INDEX ix_player_season_pitching_stats_pk
            ON player_season_pitching_stats (player_id, season, team_id)
            NULLS NOT DISTINCT;
    """)
