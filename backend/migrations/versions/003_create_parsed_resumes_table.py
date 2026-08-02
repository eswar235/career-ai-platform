"""Create parsed_resumes table

Revision ID: 003
Revises: 002_create_resumes_table
Create Date: 2024-12-20 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "003"
down_revision = "002_create_resumes_table"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create parsed_resumes table
    op.create_table(
        "parsed_resumes",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("resume_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        
        # Personal Information
        sa.Column("full_name", sa.String(255), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("location", sa.String(255), nullable=True),
        
        # Professional Summary
        sa.Column("summary", sa.Text(), nullable=True),
        
        # Structured Data (JSON)
        sa.Column("skills", postgresql.JSON(), nullable=True),
        sa.Column("experience", postgresql.JSON(), nullable=True),
        sa.Column("education", postgresql.JSON(), nullable=True),
        sa.Column("certifications", postgresql.JSON(), nullable=True),
        
        # Raw and Metadata
        sa.Column("raw_text", sa.Text(), nullable=True),
        sa.Column("confidence_score", sa.Integer(), nullable=True),
        sa.Column("quality_notes", sa.Text(), nullable=True),
        sa.Column("is_confirmed", sa.Boolean(), nullable=False, server_default="false"),
        
        # Timestamps
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        
        # Foreign Keys
        sa.ForeignKeyConstraint(["resume_id"], ["resumes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("resume_id", name="uq_parsed_resumes_resume_id"),
    )

    # Create indices
    op.create_index(op.f("ix_parsed_resumes_id"), "parsed_resumes", ["id"], unique=False)
    op.create_index(op.f("ix_parsed_resumes_resume_id"), "parsed_resumes", ["resume_id"], unique=False)
    op.create_index(op.f("ix_parsed_resumes_user_id"), "parsed_resumes", ["user_id"], unique=False)
    op.create_index(op.f("ix_parsed_resumes_created_at"), "parsed_resumes", ["created_at"], unique=False)


def downgrade() -> None:
    # Drop indices
    op.drop_index(op.f("ix_parsed_resumes_created_at"), table_name="parsed_resumes")
    op.drop_index(op.f("ix_parsed_resumes_user_id"), table_name="parsed_resumes")
    op.drop_index(op.f("ix_parsed_resumes_resume_id"), table_name="parsed_resumes")
    op.drop_index(op.f("ix_parsed_resumes_id"), table_name="parsed_resumes")

    # Drop table
    op.drop_table("parsed_resumes")
