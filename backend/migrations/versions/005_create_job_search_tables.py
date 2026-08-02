"""Create job search tables

Revision ID: 005
Revises: 004
Create Date: 2024-12-20 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Jobs table
    op.create_table(
        "jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("company_name", sa.String(255), nullable=False),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("location", sa.String(255), nullable=True),
        sa.Column("job_type", sa.String(50), nullable=True),
        sa.Column("salary_min", sa.Integer(), nullable=True),
        sa.Column("salary_max", sa.Integer(), nullable=True),
        sa.Column("salary_currency", sa.String(3), nullable=True, server_default="USD"),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("requirements", sa.Text(), nullable=True),
        sa.Column("benefits", sa.Text(), nullable=True),
        sa.Column("industry", sa.String(100), nullable=True),
        sa.Column("experience_level", sa.String(50), nullable=True),
        sa.Column("skills_required", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("posted_date", sa.Date(), nullable=False),
        sa.Column("application_deadline", sa.Date(), nullable=True),
        sa.Column("source", sa.String(100), nullable=True),
        sa.Column("source_url", sa.String(500), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_jobs_id", "jobs", ["id"])
    op.create_index("ix_jobs_title", "jobs", ["title"])
    op.create_index("ix_jobs_company_name", "jobs", ["company_name"])
    op.create_index("ix_jobs_location", "jobs", ["location"])
    op.create_index("ix_jobs_is_active", "jobs", ["is_active"])
    op.create_index("ix_jobs_posted_date", "jobs", ["posted_date"])

    # Saved jobs table
    op.create_table(
        "saved_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("saved_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "job_id", name="uq_saved_jobs"),
    )
    op.create_index("ix_saved_jobs_id", "saved_jobs", ["id"])
    op.create_index("ix_saved_jobs_user_id", "saved_jobs", ["user_id"])
    op.create_index("ix_saved_jobs_job_id", "saved_jobs", ["job_id"])

    # Job search history table
    op.create_table(
        "job_search_history",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("search_query", sa.String(255), nullable=True),
        sa.Column("filters_applied", postgresql.JSON(), nullable=True),
        sa.Column("results_count", sa.Integer(), nullable=True),
        sa.Column("searched_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_job_search_history_id", "job_search_history", ["id"])
    op.create_index("ix_job_search_history_user_id", "job_search_history", ["user_id"])
    op.create_index("ix_job_search_history_searched_at", "job_search_history", ["searched_at"])

    # Job applications table
    op.create_table(
        "job_applications",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="applied"),
        sa.Column("applied_date", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "job_id", name="uq_job_applications"),
    )
    op.create_index("ix_job_applications_id", "job_applications", ["id"])
    op.create_index("ix_job_applications_user_id", "job_applications", ["user_id"])
    op.create_index("ix_job_applications_job_id", "job_applications", ["job_id"])
    op.create_index("ix_job_applications_status", "job_applications", ["status"])


def downgrade() -> None:
    op.drop_index("ix_job_applications_status", table_name="job_applications")
    op.drop_index("ix_job_applications_job_id", table_name="job_applications")
    op.drop_index("ix_job_applications_user_id", table_name="job_applications")
    op.drop_index("ix_job_applications_id", table_name="job_applications")
    op.drop_table("job_applications")

    op.drop_index("ix_job_search_history_searched_at", table_name="job_search_history")
    op.drop_index("ix_job_search_history_user_id", table_name="job_search_history")
    op.drop_index("ix_job_search_history_id", table_name="job_search_history")
    op.drop_table("job_search_history")

    op.drop_index("ix_saved_jobs_job_id", table_name="saved_jobs")
    op.drop_index("ix_saved_jobs_user_id", table_name="saved_jobs")
    op.drop_index("ix_saved_jobs_id", table_name="saved_jobs")
    op.drop_table("saved_jobs")

    op.drop_index("ix_jobs_posted_date", table_name="jobs")
    op.drop_index("ix_jobs_is_active", table_name="jobs")
    op.drop_index("ix_jobs_location", table_name="jobs")
    op.drop_index("ix_jobs_company_name", table_name="jobs")
    op.drop_index("ix_jobs_title", table_name="jobs")
    op.drop_index("ix_jobs_id", table_name="jobs")
    op.drop_table("jobs")
