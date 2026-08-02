"""Create resumes table

Revision ID: 002
Revises: 001_create_users_table
Create Date: 2024-12-20 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "002"
down_revision = "001_create_users_table"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create resumes table
    op.create_table(
        "resumes",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("original_filename", sa.String(255), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("storage_path", sa.String(500), nullable=False),
        sa.Column("mime_type", sa.String(50), nullable=False, server_default="application/pdf"),
        sa.Column("version", sa.String(50), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("parsing_status", sa.String(50), nullable=False, server_default="pending"),
        sa.Column("parsing_error", sa.String(500), nullable=True),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("parsed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indices
    op.create_index(op.f("ix_resumes_id"), "resumes", ["id"], unique=False)
    op.create_index(op.f("ix_resumes_user_id"), "resumes", ["user_id"], unique=False)
    op.create_index(op.f("ix_resumes_uploaded_at"), "resumes", ["uploaded_at"], unique=False)


def downgrade() -> None:
    # Drop indices
    op.drop_index(op.f("ix_resumes_uploaded_at"), table_name="resumes")
    op.drop_index(op.f("ix_resumes_user_id"), table_name="resumes")
    op.drop_index(op.f("ix_resumes_id"), table_name="resumes")

    # Drop table
    op.drop_table("resumes")
