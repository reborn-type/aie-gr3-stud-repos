"""alter appeals text column to text

Revision ID: 20260529_0002
Revises: 20260526_0001
Create Date: 2026-05-29
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260529_0002"
down_revision: Union[str, None] = "20260526_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "appeals",
        "text",
        existing_type=sa.String(length=255),
        type_=sa.Text(),
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "appeals",
        "text",
        existing_type=sa.Text(),
        type_=sa.String(length=255),
        existing_nullable=False,
    )
