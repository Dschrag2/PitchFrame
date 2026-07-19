"""fix pitch count check constraint ranges

Revision ID: 66a511287c3a
Revises: 27efe10ec7fe
Create Date: 2026-07-18 22:53:43.216635

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '66a511287c3a'
down_revision: Union[str, Sequence[str], None] = '27efe10ec7fe'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint("ck_pitches_balls_range", "pitches", type_="check")
    op.drop_constraint("ck_pitches_strikes_range", "pitches", type_="check")
    op.drop_constraint("ck_pitches_outs_range", "pitches", type_="check")
    op.create_check_constraint("ck_pitches_balls_range", "pitches", "balls BETWEEN 0 AND 4")
    op.create_check_constraint("ck_pitches_strikes_range", "pitches", "strikes BETWEEN 0 AND 3")
    op.create_check_constraint("ck_pitches_outs_range", "pitches", "outs BETWEEN 0 AND 3")


def downgrade() -> None:
    op.drop_constraint("ck_pitches_balls_range", "pitches", type_="check")
    op.drop_constraint("ck_pitches_strikes_range", "pitches", type_="check")
    op.drop_constraint("ck_pitches_outs_range", "pitches", type_="check")
    op.create_check_constraint("ck_pitches_balls_range", "pitches", "balls BETWEEN 0 AND 3")
    op.create_check_constraint("ck_pitches_strikes_range", "pitches", "strikes BETWEEN 0 AND 2")
    op.create_check_constraint("ck_pitches_outs_range", "pitches", "outs BETWEEN 0 AND 2")
