"""add age and income_stability to users

Skor tutarlılığı: quiz sırasında yaş ve gelir istikrarı skoru etkiliyordu
ama DB'ye yazılmıyordu — GET /profile aynı kullanıcı için FARKLI skor
hesaplıyordu (örn. 6.2 → 5.7). İki alan da kalıcı hale getirildi.

Revision ID: a1c9e4b20d51
Revises: 38f539c3549e
Create Date: 2026-07-10

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1c9e4b20d51'
down_revision: Union[str, None] = '38f539c3549e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('age', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('income_stability', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'income_stability')
    op.drop_column('users', 'age')
