"""add file hash to documents

Revision ID: b13228f5500a
Revises: 8d52e6f48cd4
Create Date: 2026-10-04
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b13228f5500a"
down_revision: Union[str, Sequence[str], None] = "8d52e6f48cd4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        op.f("ix_documents_file_hash"),
        "documents",
        ["file_hash"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_documents_file_hash"),
        table_name="documents",
    )