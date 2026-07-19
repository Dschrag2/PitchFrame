"""add movement_index to baserunning_events for multi-leg movements

Revision ID: aacab03e91bd
Revises: 9759f768c409
Create Date: 2026-07-18 22:57:49.896406

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'aacab03e91bd'
down_revision: Union[str, Sequence[str], None] = '9759f768c409'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('baserunning_events', sa.Column('movement_index', sa.SmallInteger(), nullable=False))
    op.add_column('baserunning_event_credits', sa.Column('movement_index', sa.SmallInteger(), nullable=False))

    op.drop_constraint('baserunning_event_credits_game_id_at_bat_index_event_index_fkey', 'baserunning_event_credits', type_='foreignkey')
    op.drop_constraint('baserunning_event_credits_pkey', 'baserunning_event_credits', type_='primary')
    op.drop_constraint('baserunning_events_pkey', 'baserunning_events', type_='primary')

    op.create_primary_key(
        'baserunning_events_pkey', 'baserunning_events',
        ['game_id', 'at_bat_index', 'event_index', 'runner_id', 'movement_index'],
    )
    op.create_primary_key(
        'baserunning_event_credits_pkey', 'baserunning_event_credits',
        ['game_id', 'at_bat_index', 'event_index', 'runner_id', 'movement_index', 'credit_index'],
    )
    op.create_foreign_key(
        None, 'baserunning_event_credits', 'baserunning_events',
        ['game_id', 'at_bat_index', 'event_index', 'runner_id', 'movement_index'],
        ['game_id', 'at_bat_index', 'event_index', 'runner_id', 'movement_index'],
        ondelete='CASCADE',
    )


def downgrade() -> None:
    op.drop_constraint('baserunning_event_credits_game_id_at_bat_index_event_index_movement_index_fkey', 'baserunning_event_credits', type_='foreignkey')
    op.drop_constraint('baserunning_event_credits_pkey', 'baserunning_event_credits', type_='primary')
    op.drop_constraint('baserunning_events_pkey', 'baserunning_events', type_='primary')

    op.drop_column('baserunning_events', 'movement_index')
    op.drop_column('baserunning_event_credits', 'movement_index')

    op.create_primary_key(
        'baserunning_events_pkey', 'baserunning_events',
        ['game_id', 'at_bat_index', 'event_index', 'runner_id'],
    )
    op.create_primary_key(
        'baserunning_event_credits_pkey', 'baserunning_event_credits',
        ['game_id', 'at_bat_index', 'event_index', 'runner_id', 'credit_index'],
    )
    op.create_foreign_key(
        'baserunning_event_credits_game_id_at_bat_index_event_index_fkey', 'baserunning_event_credits', 'baserunning_events',
        ['game_id', 'at_bat_index', 'event_index', 'runner_id'],
        ['game_id', 'at_bat_index', 'event_index', 'runner_id'],
        ondelete='CASCADE',
    )
