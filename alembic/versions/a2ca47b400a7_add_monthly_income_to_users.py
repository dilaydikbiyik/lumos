"""add monthly_income to users

Revision ID: a2ca47b400a7
Revises: b7f3d2e91a04
Create Date: 2026-07-16
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a2ca47b400a7'
down_revision: Union[str, None] = 'b7f3d2e91a04'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('monthly_income', sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'monthly_income')
