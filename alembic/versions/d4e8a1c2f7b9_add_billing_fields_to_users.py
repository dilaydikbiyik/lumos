"""add billing fields to users

Revision ID: d4e8a1c2f7b9
Revises: cfa2dce6239f
Create Date: 2026-11-21
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "d4e8a1c2f7b9"
down_revision: Union[str, None] = "cfa2dce6239f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("users") as batch:
        batch.add_column(sa.Column("plan_source", sa.String(), nullable=True))
        batch.add_column(sa.Column("subscription_id", sa.String(), nullable=True))
        batch.add_column(sa.Column("billing_portal_url", sa.String(), nullable=True))
        batch.add_column(sa.Column("plan_ends_at", sa.String(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("users") as batch:
        batch.drop_column("plan_ends_at")
        batch.drop_column("billing_portal_url")
        batch.drop_column("subscription_id")
        batch.drop_column("plan_source")
