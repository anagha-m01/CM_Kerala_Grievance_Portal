"""Initial schema for grievance portal.

Revision ID: 0001_initial
Revises:
Create Date: 2026-11-11
"""
from alembic import op
from app.db.session import Base
from app.models import entities  # noqa: F401

revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Metadata remains the single source of truth for the initial schema.
    Base.metadata.create_all(bind=op.get_bind())


def downgrade():
    Base.metadata.drop_all(bind=op.get_bind())
