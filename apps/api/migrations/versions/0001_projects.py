"""Initial projects table."""

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "projects",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("title", sa.String(120), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="created"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.CheckConstraint("length(trim(title)) BETWEEN 1 AND 120", name="title_length"),
        sa.CheckConstraint(
            "length(trim(description)) BETWEEN 1 AND 10000", name="description_length"
        ),
        sa.CheckConstraint("status = 'created'", name="project_status"),
    )


def downgrade():
    op.drop_table("projects")
