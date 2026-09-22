"""mnd is not nullable anymore

Revision ID: 273d97b32977
Revises: 46ba15d41531
Create Date: 2026-09-21 01:55:15.363759

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '273d97b32977'
down_revision: Union[str, Sequence[str], None] = '46ba15d41531'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "users",
        "mnd",
        existing_type=sa.String(),
        nullable=False
    )


def downgrade() -> None:
    op.alter_column(
        "users",
        "mnd",
        existing_type=sa.String(),
        nullable=True
    )