"""Create chat access table.

Revision ID: 202409300001
Revises:
Create Date: 2024-09-30 00:01:00.000000
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "202409300001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "chat_access",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("chat_id", sa.String(), nullable=False),
        sa.Column("allowed", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("chat_id"),
    )


def downgrade() -> None:
    op.drop_table("chat_access")
