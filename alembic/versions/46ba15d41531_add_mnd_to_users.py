"""add mnd to users

Revision ID: 46ba15d41531
Revises: 98d31ca56128
Create Date: 2026-09-21 01:49:43.963085

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '46ba15d41531'
down_revision: Union[str, Sequence[str], None] = '98d31ca56128'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "users",
        sa.Column("mnd", sa.String(), nullable=True)
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column(
        "users",
        "mnd"
    )
