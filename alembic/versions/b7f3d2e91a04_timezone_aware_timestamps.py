"""timezone-aware timestamps on users and holdings

The ORM defaults produce timezone-aware UTC datetimes, but the columns
were plain TIMESTAMP (naive). SQLite tolerated it; asyncpg/Postgres
rejected EVERY insert in production ("can't subtract offset-naive and
offset-aware datetimes") — no user row could ever be created.

Revision ID: b7f3d2e91a04
Revises: a1c9e4b20d51
Create Date: 2026-07-12

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b7f3d2e91a04'
down_revision: Union[str, None] = 'a1c9e4b20d51'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_TABLES = ("users", "holdings")


def upgrade() -> None:
    # batch mode: no-op wrapper on Postgres, required for SQLite ALTERs
    for table in _TABLES:
        with op.batch_alter_table(table) as batch:
            batch.alter_column(
                "created_at",
                type_=sa.DateTime(timezone=True),
                existing_type=sa.DateTime(),
                postgresql_using="created_at AT TIME ZONE 'UTC'",
            )
            batch.alter_column(
                "updated_at",
                type_=sa.DateTime(timezone=True),
                existing_type=sa.DateTime(),
                postgresql_using="updated_at AT TIME ZONE 'UTC'",
            )


def downgrade() -> None:
    for table in _TABLES:
        with op.batch_alter_table(table) as batch:
            batch.alter_column("created_at", type_=sa.DateTime(), existing_type=sa.DateTime(timezone=True))
            batch.alter_column("updated_at", type_=sa.DateTime(), existing_type=sa.DateTime(timezone=True))
