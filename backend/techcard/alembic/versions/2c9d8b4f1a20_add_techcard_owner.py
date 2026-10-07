"""add techcard owner

Revision ID: 2c9d8b4f1a20
Revises: 7803079bd1e8
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "2c9d8b4f1a20"
down_revision: Union[str, Sequence[str], None] = "7803079bd1e8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("tech_cards", sa.Column("owner_id", sa.Integer(), nullable=True))
    op.create_index("ix_tech_cards_owner_id", "tech_cards", ["owner_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_tech_cards_owner_id", table_name="tech_cards")
    op.drop_column("tech_cards", "owner_id")
