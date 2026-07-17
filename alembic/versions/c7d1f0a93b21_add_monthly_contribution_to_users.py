"""add monthly_contribution to users

Revision ID: c7d1f0a93b21
Revises: a2ca47b400a7
Create Date: 2026-07-16
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c7d1f0a93b21'
down_revision: Union[str, None] = 'a2ca47b400a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('monthly_contribution', sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'monthly_contribution')
