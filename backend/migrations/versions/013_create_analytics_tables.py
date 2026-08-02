"""
Create analytics and dashboard tables
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "013"
down_revision = "012"
branch_labels = None
depends_on = None


def upgrade():
    """Create analytics tables"""
    
    # Application Statistics (cached/aggregated data)
    op.create_table(
        "application_statistics",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("total_submitted", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("total_pending", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("total_rejected", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("total_interviews", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("total_offers", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("response_rate", sa.Float(), nullable=True),
        sa.Column("average_response_time_days", sa.Float(), nullable=True),
        sa.Column("success_rate", sa.Float(), nullable=True),
        sa.Column("last_updated", sa.DateTime(), nullable=True, server_default=sa.func.now()),
        sa.Column("created_at", sa.DateTime(), nullable=True, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index("idx_app_stats_user_id", "application_statistics", ["user_id"])

    # Application Trends (time-series data)
    op.create_table(
        "application_trends",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("applications_submitted", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("applications_reviewed", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("interviews_scheduled", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("rejections_received", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("offers_received", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=True, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "date"),
    )
    op.create_index("idx_trends_user_id_date", "application_trends", ["user_id", "date"])

    # Job Analytics (per-job statistics)
    op.create_table(
        "job_analytics",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("application_count", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("job_title", sa.String(255), nullable=True),
        sa.Column("company_name", sa.String(255), nullable=True),
        sa.Column("job_source", sa.String(100), nullable=True),
        sa.Column("experience_level", sa.String(50), nullable=True),
        sa.Column("applications_submitted", sa.Integer(), nullable=True, server_default="1"),
        sa.Column("date_applied", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_job_analytics_user_id", "job_analytics", ["user_id"])
    op.create_index("idx_job_analytics_job_id", "job_analytics", ["job_id"])

    # Role Analytics (aggregated by role)
    op.create_table(
        "role_analytics",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("job_title", sa.String(255), nullable=False),
        sa.Column("application_count", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("interview_count", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("offer_count", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("rejection_count", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("last_applied", sa.Date(), nullable=True),
        sa.Column("success_rate", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=True, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "job_title"),
    )
    op.create_index("idx_role_analytics_user_id", "role_analytics", ["user_id"])

    # Company Analytics (aggregated by company)
    op.create_table(
        "company_analytics",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("company_name", sa.String(255), nullable=False),
        sa.Column("application_count", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("interview_count", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("offer_count", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("rejection_count", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("last_applied", sa.Date(), nullable=True),
        sa.Column("success_rate", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=True, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "company_name"),
    )
    op.create_index("idx_company_analytics_user_id", "company_analytics", ["user_id"])

    # Source Analytics (by job source)
    op.create_table(
        "source_analytics",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_name", sa.String(100), nullable=False),
        sa.Column("application_count", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("interview_count", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("offer_count", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("rejection_count", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("success_rate", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=True, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "source_name"),
    )
    op.create_index("idx_source_analytics_user_id", "source_analytics", ["user_id"])


def downgrade():
    """Drop analytics tables"""
    op.drop_index("idx_source_analytics_user_id", table_name="source_analytics")
    op.drop_table("source_analytics")
    
    op.drop_index("idx_company_analytics_user_id", table_name="company_analytics")
    op.drop_table("company_analytics")
    
    op.drop_index("idx_role_analytics_user_id", table_name="role_analytics")
    op.drop_table("role_analytics")
    
    op.drop_index("idx_job_analytics_job_id", table_name="job_analytics")
    op.drop_index("idx_job_analytics_user_id", table_name="job_analytics")
    op.drop_table("job_analytics")
    
    op.drop_index("idx_trends_user_id_date", table_name="application_trends")
    op.drop_table("application_trends")
    
    op.drop_index("idx_app_stats_user_id", table_name="application_statistics")
    op.drop_table("application_statistics")
