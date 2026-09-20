"""add monthly outgoings to users

Rent plus essential monthly costs. The reserve in `budget_split` is six
months of OUTGOINGS, and until now the router handed it `monthly_income`
instead — so someone earning 40,000 and spending 15,000 was told to hold
back 240,000 rather than 90,000, and the whole plan shrank behind it.
Income and spending are different numbers and the app has to ask for both.

Revision ID: b3f91c27d504
Revises: 8a5213176a8a
Create Date: 2026-09-20

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b3f91c27d504'
down_revision: Union[str, None] = '8a5213176a8a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('monthly_outgoings', sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'monthly_outgoings')
