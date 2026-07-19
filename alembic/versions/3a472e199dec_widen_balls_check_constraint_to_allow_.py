"""widen balls check constraint to allow observed data anomaly

Revision ID: 3a472e199dec
Revises: aacab03e91bd
Create Date: 2026-07-19 09:42:08.909001

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3a472e199dec'
down_revision: Union[str, Sequence[str], None] = 'aacab03e91bd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint("ck_pitches_balls_range", "pitches", type_="check")
    op.create_check_constraint("ck_pitches_balls_range", "pitches", "balls BETWEEN 0 AND 5")


def downgrade() -> None:
    op.drop_constraint("ck_pitches_balls_range", "pitches", type_="check")
    op.create_check_constraint("ck_pitches_balls_range", "pitches", "balls BETWEEN 0 AND 4")
