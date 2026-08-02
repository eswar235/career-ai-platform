"""Create resume optimization tables

Revision ID: 007
Revises: 006
Create Date: 2024-12-20 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "007"
down_revision = "006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Resume optimizations table
    op.create_table(
        "resume_optimizations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("original_content", sa.Text(), nullable=False),
        sa.Column("optimized_content", sa.Text(), nullable=True),
        sa.Column("ats_score", sa.Integer(), nullable=True),
        sa.Column("keyword_score", sa.Integer(), nullable=True),
        sa.Column("formatting_score", sa.Integer(), nullable=True),
        sa.Column("readability_score", sa.Integer(), nullable=True),
        sa.Column("overall_score", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", name="uq_resume_optimizations_user_id"),
    )
    op.create_index("ix_resume_optimizations_id", "resume_optimizations", ["id"])
    op.create_index("ix_resume_optimizations_user_id", "resume_optimizations", ["user_id"])

    # Tailored resumes table
    op.create_table(
        "tailored_resumes",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tailored_content", sa.Text(), nullable=False),
        sa.Column("match_keywords", sa.Integer(), nullable=True),
        sa.Column("ats_score", sa.Integer(), nullable=True),
        sa.Column("keyword_score", sa.Integer(), nullable=True),
        sa.Column("recommendations", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "job_id", name="uq_tailored_resumes"),
    )
    op.create_index("ix_tailored_resumes_id", "tailored_resumes", ["id"])
    op.create_index("ix_tailored_resumes_user_id", "tailored_resumes", ["user_id"])
    op.create_index("ix_tailored_resumes_job_id", "tailored_resumes", ["job_id"])

    # Optimization suggestions table
    op.create_table(
        "optimization_suggestions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("optimization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("suggestion", sa.Text(), nullable=False),
        sa.Column("priority", sa.String(20), nullable=False),
        sa.Column("impact_score", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["optimization_id"], ["resume_optimizations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_optimization_suggestions_id", "optimization_suggestions", ["id"])
    op.create_index("ix_optimization_suggestions_optimization_id", "optimization_suggestions", ["optimization_id"])


def downgrade() -> None:
    op.drop_index("ix_optimization_suggestions_optimization_id", table_name="optimization_suggestions")
    op.drop_index("ix_optimization_suggestions_id", table_name="optimization_suggestions")
    op.drop_table("optimization_suggestions")

    op.drop_index("ix_tailored_resumes_job_id", table_name="tailored_resumes")
    op.drop_index("ix_tailored_resumes_user_id", table_name="tailored_resumes")
    op.drop_index("ix_tailored_resumes_id", table_name="tailored_resumes")
    op.drop_table("tailored_resumes")

    op.drop_index("ix_resume_optimizations_user_id", table_name="resume_optimizations")
    op.drop_index("ix_resume_optimizations_id", table_name="resume_optimizations")
    op.drop_table("resume_optimizations")
