"""restore the legacy techcard reference schema

Revision ID: 71ac4e8d2f60
Revises: 2c9d8b4f1a20
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "71ac4e8d2f60"
down_revision: Union[str, Sequence[str], None] = "2c9d8b4f1a20"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "name_teacher",
        sa.Column("primary_key", sa.Integer(), primary_key=True),
        sa.Column("full_name", sa.Text(), nullable=False),
    )
    op.create_table(
        "lesson_type",
        sa.Column("primary_key", sa.Integer(), primary_key=True),
        sa.Column("lesson_type", sa.Text(), nullable=False),
    )
    op.create_table(
        "group_name",
        sa.Column("primary_key", sa.Integer(), primary_key=True),
        # The source stores curator IDs as TEXT although teacher IDs are INTEGER.
        sa.Column("curator_group", sa.Text()),
        sa.Column("group_name", sa.Text()),
    )
    op.create_table(
        "lesson",
        sa.Column("primary_key", sa.Integer(), primary_key=True),
        sa.Column("name_lesson", sa.Text(), nullable=False),
        sa.Column("Teacher", sa.Integer()),
        sa.Column("Group_name", sa.Integer()),
        sa.Column("type_lesson", sa.Integer()),
    )
    op.create_table(
        "learning_outcomes",
        sa.Column("primary_key", sa.Integer(), primary_key=True),
        sa.Column("lesson", sa.Integer()),
        sa.Column("skill", sa.Text()),
        sa.Column("know", sa.Text()),
    )
    op.create_table(
        "lesson_topic",
        sa.Column("primary_key", sa.Integer(), primary_key=True),
        sa.Column(
            "lesson",
            sa.Integer(),
            sa.ForeignKey("lesson.primary_key"),
        ),
        sa.Column("topic", sa.Text()),
    )
    op.create_table(
        "pk_and_ok",
        sa.Column("primary_key", sa.Integer(), primary_key=True),
        sa.Column(
            "lesson",
            sa.Integer(),
            sa.ForeignKey("lesson.primary_key"),
        ),
        sa.Column("prof_comp", sa.Text()),
        sa.Column("general_comp", sa.Text()),
    )
    op.create_table(
        "skills_and_Knowledge",
        sa.Column("primary_key", sa.Integer(), primary_key=True),
        sa.Column("lesson", sa.Integer()),
        sa.Column("skill", sa.Text()),
        sa.Column("knowledge", sa.Text()),
    )


def downgrade() -> None:
    op.drop_table("skills_and_Knowledge")
    op.drop_table("pk_and_ok")
    op.drop_table("lesson_topic")
    op.drop_table("learning_outcomes")
    op.drop_table("lesson")
    op.drop_table("group_name")
    op.drop_table("lesson_type")
    op.drop_table("name_teacher")
