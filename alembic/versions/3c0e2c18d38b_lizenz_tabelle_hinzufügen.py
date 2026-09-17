"""Lizenz-tabelle hinzufügen

Revision ID: 3c0e2c18d38b
Revises: 16484d721627
Create Date: 2026-09-17 17:46:59.540194

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3c0e2c18d38b'
down_revision: Union[str, Sequence[str], None] = '16484d721627'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "lizenzen",
        sa.Column("id", sa.INTEGER(), primary_key=True),
        sa.Column("user_id", sa.INTEGER(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("valid_from", sa.DATE(), nullable=False),
        sa.Column("valid_until", sa.DATE(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False )
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("lizenzen")
