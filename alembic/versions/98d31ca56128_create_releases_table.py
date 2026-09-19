"""create releases table

Revision ID: 98d31ca56128
Revises: 3c0e2c18d38b
Create Date: 2026-09-19 19:42:51.444093

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '98d31ca56128'
down_revision: Union[str, Sequence[str], None] = '3c0e2c18d38b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "releases",
        sa.Column("version", sa.String(), primary_key=True),
        sa.Column("release_date", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("size", sa.Integer(), nullable=False),
        sa.Column("location", sa.String(), nullable=False),
        sa.Column("checksum", sa.String(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.false())

    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table(
        "releases"
    )
