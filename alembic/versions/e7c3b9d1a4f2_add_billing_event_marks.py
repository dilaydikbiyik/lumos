"""add billing_event_marks to users

The last applied store event's timestamp per store, so a late retry cannot
undo a newer event.

Revision ID: e7c3b9d1a4f2
Revises: d4e8a1c2f7b9
Create Date: 2026-11-25
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "e7c3b9d1a4f2"
down_revision: Union[str, None] = "d4e8a1c2f7b9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("users") as batch:
        batch.add_column(sa.Column("billing_event_marks", sa.JSON(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("users") as batch:
        batch.drop_column("billing_event_marks")
