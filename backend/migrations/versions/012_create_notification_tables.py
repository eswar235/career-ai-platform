"""
Create notification and job alert tables
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "012"
down_revision = "011"
branch_labels = None
depends_on = None


def upgrade():
    """Create notification tables"""
    
    # Job Alerts table
    op.create_table(
        "job_alerts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("keywords", sa.Text(), nullable=True),
        sa.Column("locations", postgresql.JSON(), nullable=True),
        sa.Column("job_titles", postgresql.JSON(), nullable=True),
        sa.Column("experience_levels", postgresql.JSON(), nullable=True),
        sa.Column("salary_min", sa.Integer(), nullable=True),
        sa.Column("salary_max", sa.Integer(), nullable=True),
        sa.Column("min_match_score", sa.Float(), nullable=True, server_default="60"),
        sa.Column("notification_frequency", sa.String(50), nullable=True, server_default="daily"),
        sa.Column("preferred_time", sa.Time(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True, server_default="true"),
        sa.Column("created_at", sa.DateTime(), nullable=True, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=True, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index("idx_job_alerts_user_id", "job_alerts", ["user_id"])
    op.create_index("idx_job_alerts_is_active", "job_alerts", ["is_active"])

    # Notifications table
    op.create_table(
        "notifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("notification_type", sa.String(50), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("related_entity_type", sa.String(50), nullable=True),
        sa.Column("related_entity_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("is_read", sa.Boolean(), nullable=True, server_default="false"),
        sa.Column("read_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=True, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_notifications_user_id", "notifications", ["user_id"])
    op.create_index("idx_notifications_is_read", "notifications", ["is_read"])
    op.create_index("idx_notifications_created_at", "notifications", ["created_at"])

    # Email Notifications table
    op.create_table(
        "email_notifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email_address", sa.String(255), nullable=False),
        sa.Column("notification_type", sa.String(50), nullable=False),
        sa.Column("subject", sa.String(255), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("status", sa.String(50), nullable=True, server_default="pending"),
        sa.Column("sent_at", sa.DateTime(), nullable=True),
        sa.Column("delivery_error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=True, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_email_notifications_user_id", "email_notifications", ["user_id"])
    op.create_index("idx_email_notifications_status", "email_notifications", ["status"])

    # Alert Job Matches table (for tracking which jobs matched an alert)
    op.create_table(
        "alert_job_matches",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("alert_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("match_score", sa.Float(), nullable=True),
        sa.Column("notification_sent", sa.Boolean(), nullable=True, server_default="false"),
        sa.Column("user_dismissed", sa.Boolean(), nullable=True, server_default="false"),
        sa.Column("created_at", sa.DateTime(), nullable=True, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["alert_id"], ["job_alerts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("alert_id", "job_id"),
    )
    op.create_index("idx_alert_job_matches_alert_id", "alert_job_matches", ["alert_id"])
    op.create_index("idx_alert_job_matches_job_id", "alert_job_matches", ["job_id"])
    op.create_index("idx_alert_job_matches_notification_sent", "alert_job_matches", ["notification_sent"])

    # Notification Preferences table
    op.create_table(
        "notification_preferences",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("job_alerts_enabled", sa.Boolean(), nullable=True, server_default="true"),
        sa.Column("application_updates_enabled", sa.Boolean(), nullable=True, server_default="true"),
        sa.Column("interview_reminders_enabled", sa.Boolean(), nullable=True, server_default="true"),
        sa.Column("daily_digest_enabled", sa.Boolean(), nullable=True, server_default="false"),
        sa.Column("digest_time", sa.Time(), nullable=True),
        sa.Column("email_notifications_enabled", sa.Boolean(), nullable=True, server_default="true"),
        sa.Column("in_app_notifications_enabled", sa.Boolean(), nullable=True, server_default="true"),
        sa.Column("created_at", sa.DateTime(), nullable=True, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=True, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index("idx_notification_preferences_user_id", "notification_preferences", ["user_id"])


def downgrade():
    """Drop notification tables"""
    op.drop_index("idx_notification_preferences_user_id", table_name="notification_preferences")
    op.drop_table("notification_preferences")
    
    op.drop_index("idx_alert_job_matches_notification_sent", table_name="alert_job_matches")
    op.drop_index("idx_alert_job_matches_job_id", table_name="alert_job_matches")
    op.drop_index("idx_alert_job_matches_alert_id", table_name="alert_job_matches")
    op.drop_table("alert_job_matches")
    
    op.drop_index("idx_email_notifications_status", table_name="email_notifications")
    op.drop_index("idx_email_notifications_user_id", table_name="email_notifications")
    op.drop_table("email_notifications")
    
    op.drop_index("idx_notifications_created_at", table_name="notifications")
    op.drop_index("idx_notifications_is_read", table_name="notifications")
    op.drop_index("idx_notifications_user_id", table_name="notifications")
    op.drop_table("notifications")
    
    op.drop_index("idx_job_alerts_is_active", table_name="job_alerts")
    op.drop_index("idx_job_alerts_user_id", table_name="job_alerts")
    op.drop_table("job_alerts")
