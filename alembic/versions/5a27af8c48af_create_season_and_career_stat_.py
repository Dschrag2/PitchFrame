"""create season and career stat materialized views

Revision ID: 5a27af8c48af
Revises: 3a472e199dec
Create Date: 2026-07-19 10:07:07.608662

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5a27af8c48af'
down_revision: Union[str, Sequence[str], None] = '3a472e199dec'
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


def upgrade() -> None:
    batting_sums = _sum_lines(BATTING_SUM_COLS, "b")
    pitching_sums = _sum_lines(PITCHING_SUM_COLS, "p")

    op.execute(f"""
        CREATE MATERIALIZED VIEW player_season_batting_stats AS
        SELECT
            b.player_id,
            g.season,
            b.team_id,
            {batting_sums},
            {BATTING_RATE_STATS.strip()}
        FROM batting_boxscores b
        JOIN games g ON g.id = b.game_id
        GROUP BY b.player_id, g.season, b.team_id

        UNION ALL

        SELECT
            b.player_id,
            g.season,
            NULL::integer AS team_id,
            {batting_sums},
            {BATTING_RATE_STATS.strip()}
        FROM batting_boxscores b
        JOIN games g ON g.id = b.game_id
        GROUP BY b.player_id, g.season
        HAVING COUNT(DISTINCT b.team_id) > 1;
    """)
    op.execute("""
        CREATE UNIQUE INDEX ix_player_season_batting_stats_pk
            ON player_season_batting_stats (player_id, season, team_id)
            NULLS NOT DISTINCT;
    """)

    op.execute(f"""
        CREATE MATERIALIZED VIEW player_season_pitching_stats AS
        SELECT
            p.player_id,
            g.season,
            p.team_id,
            {pitching_sums},
            {PITCHING_RATE_STATS.strip()}
        FROM pitching_boxscores p
        JOIN games g ON g.id = p.game_id
        GROUP BY p.player_id, g.season, p.team_id

        UNION ALL

        SELECT
            p.player_id,
            g.season,
            NULL::integer AS team_id,
            {pitching_sums},
            {PITCHING_RATE_STATS.strip()}
        FROM pitching_boxscores p
        JOIN games g ON g.id = p.game_id
        GROUP BY p.player_id, g.season
        HAVING COUNT(DISTINCT p.team_id) > 1;
    """)
    op.execute("""
        CREATE UNIQUE INDEX ix_player_season_pitching_stats_pk
            ON player_season_pitching_stats (player_id, season, team_id)
            NULLS NOT DISTINCT;
    """)

    op.execute(f"""
        CREATE MATERIALIZED VIEW player_career_batting_stats AS
        SELECT
            b.player_id,
            {batting_sums},
            {BATTING_RATE_STATS.strip()}
        FROM batting_boxscores b
        GROUP BY b.player_id;
    """)
    op.execute("""
        CREATE UNIQUE INDEX ix_player_career_batting_stats_pk
            ON player_career_batting_stats (player_id);
    """)

    op.execute(f"""
        CREATE MATERIALIZED VIEW player_career_pitching_stats AS
        SELECT
            p.player_id,
            {pitching_sums},
            {PITCHING_RATE_STATS.strip()}
        FROM pitching_boxscores p
        GROUP BY p.player_id;
    """)
    op.execute("""
        CREATE UNIQUE INDEX ix_player_career_pitching_stats_pk
            ON player_career_pitching_stats (player_id);
    """)


def downgrade() -> None:
    op.execute("DROP MATERIALIZED VIEW IF EXISTS player_career_pitching_stats;")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS player_career_batting_stats;")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS player_season_pitching_stats;")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS player_season_batting_stats;")
