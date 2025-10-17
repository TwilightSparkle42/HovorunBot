"""Add provider column to chat access table

Revision ID: 202410010001
Revises: 202409300001
Create Date: 2024-10-01 00:01:00.000000
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "202410010001"
down_revision = "202409300001"
branch_labels = None
depends_on = None

DEFAULT_PROVIDER = "Infermatic"


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("chat_access")}

    if "provider" not in columns:
        with op.batch_alter_table("chat_access") as batch_op:
            batch_op.add_column(
                sa.Column("provider", sa.String(), nullable=False, server_default=DEFAULT_PROVIDER),
            )

    op.execute(
        sa.text("UPDATE chat_access SET provider = :default_provider WHERE provider IS NULL").bindparams(
            default_provider=DEFAULT_PROVIDER
        )
    )


def downgrade() -> None:
    with op.batch_alter_table("chat_access") as batch_op:
        batch_op.drop_column("provider")
