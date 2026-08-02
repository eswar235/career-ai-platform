"""
Create admin and audit tables
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "014"
down_revision = "013"
branch_labels = None
depends_on = None


def upgrade():
    """Create admin tables"""
    
    # Add is_admin column to users table
    op.add_column("users", sa.Column("is_admin", sa.Boolean(), nullable=True, server_default="false"))
    op.add_column("users", sa.Column("is_superuser", sa.Boolean(), nullable=True, server_default="false"))
    op.add_column("users", sa.Column("permissions", postgresql.JSON(), nullable=True))
    
    # Audit Log table
    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("admin_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("action_type", sa.String(100), nullable=False),
        sa.Column("entity_type", sa.String(100), nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("changes", postgresql.JSON(), nullable=True),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("ip_address", sa.String(50), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["admin_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_audit_logs_user_id", "audit_logs", ["user_id"])
    op.create_index("idx_audit_logs_admin_id", "audit_logs", ["admin_id"])
    op.create_index("idx_audit_logs_action_type", "audit_logs", ["action_type"])
    op.create_index("idx_audit_logs_created_at", "audit_logs", ["created_at"])

    # System Events table
    op.create_table(
        "system_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_type", sa.String(100), nullable=False),
        sa.Column("severity", sa.String(20), nullable=False),  # info, warning, error, critical
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("related_entity", sa.String(100), nullable=True),
        sa.Column("related_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("metadata", postgresql.JSON(), nullable=True),
        sa.Column("resolved", sa.Boolean(), nullable=True, server_default="false"),
        sa.Column("resolved_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=True, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_system_events_event_type", "system_events", ["event_type"])
    op.create_index("idx_system_events_severity", "system_events", ["severity"])
    op.create_index("idx_system_events_resolved", "system_events", ["resolved"])
    op.create_index("idx_system_events_created_at", "system_events", ["created_at"])

    # System Metrics table
    op.create_table(
        "system_metrics",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("metric_type", sa.String(100), nullable=False),
        sa.Column("value", sa.Float(), nullable=False),
        sa.Column("unit", sa.String(50), nullable=True),
        sa.Column("threshold_warning", sa.Float(), nullable=True),
        sa.Column("threshold_critical", sa.Float(), nullable=True),
        sa.Column("status", sa.String(20), nullable=True, server_default="normal"),  # normal, warning, critical
        sa.Column("metadata", postgresql.JSON(), nullable=True),
        sa.Column("recorded_at", sa.DateTime(), nullable=True, server_default=sa.func.now()),
        sa.Column("created_at", sa.DateTime(), nullable=True, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_system_metrics_metric_type", "system_metrics", ["metric_type"])
    op.create_index("idx_system_metrics_recorded_at", "system_metrics", ["recorded_at"])

    # User Suspension table
    op.create_table(
        "user_suspensions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("suspended_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("suspended_at", sa.DateTime(), nullable=True, server_default=sa.func.now()),
        sa.Column("unsuspended_at", sa.DateTime(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True, server_default="true"),
        sa.Column("created_at", sa.DateTime(), nullable=True, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["suspended_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_user_suspensions_user_id", "user_suspensions", ["user_id"])
    op.create_index("idx_user_suspensions_is_active", "user_suspensions", ["is_active"])


def downgrade():
    """Drop admin tables"""
    op.drop_index("idx_user_suspensions_is_active", table_name="user_suspensions")
    op.drop_index("idx_user_suspensions_user_id", table_name="user_suspensions")
    op.drop_table("user_suspensions")
    
    op.drop_index("idx_system_metrics_recorded_at", table_name="system_metrics")
    op.drop_index("idx_system_metrics_metric_type", table_name="system_metrics")
    op.drop_table("system_metrics")
    
    op.drop_index("idx_system_events_created_at", table_name="system_events")
    op.drop_index("idx_system_events_resolved", table_name="system_events")
    op.drop_index("idx_system_events_severity", table_name="system_events")
    op.drop_index("idx_system_events_event_type", table_name="system_events")
    op.drop_table("system_events")
    
    op.drop_index("idx_audit_logs_created_at", table_name="audit_logs")
    op.drop_index("idx_audit_logs_action_type", table_name="audit_logs")
    op.drop_index("idx_audit_logs_admin_id", table_name="audit_logs")
    op.drop_index("idx_audit_logs_user_id", table_name="audit_logs")
    op.drop_table("audit_logs")
    
    op.drop_column("users", "permissions")
    op.drop_column("users", "is_superuser")
    op.drop_column("users", "is_admin")
