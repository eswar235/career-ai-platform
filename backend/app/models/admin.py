"""
Admin and audit models
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String, Boolean, DateTime, Float, Text, ForeignKey, Index, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class AuditLog(Base):
    """Audit log for tracking admin and user actions"""
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    admin_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action_type = Column(String(100), nullable=False)  # create, update, delete, suspend, export, etc.
    entity_type = Column(String(100), nullable=False)  # user, job, application, resume, etc.
    entity_id = Column(UUID(as_uuid=True), nullable=True)
    changes = Column(JSON, nullable=True)  # What changed (old vs new values)
    reason = Column(Text, nullable=True)  # Why the action was taken
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="audit_logs_as_user")
    admin = relationship("User", foreign_keys=[admin_id], back_populates="audit_logs_as_admin")

    __table_args__ = (
        Index("idx_audit_logs_user_id", "user_id"),
        Index("idx_audit_logs_admin_id", "admin_id"),
        Index("idx_audit_logs_action_type", "action_type"),
        Index("idx_audit_logs_created_at", "created_at"),
    )


class SystemEvent(Base):
    """System-level events for monitoring"""
    __tablename__ = "system_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_type = Column(String(100), nullable=False)  # error, warning, info, security_alert, etc.
    severity = Column(String(20), nullable=False)  # info, warning, error, critical
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    related_entity = Column(String(100), nullable=True)  # user, application, system, etc.
    related_id = Column(UUID(as_uuid=True), nullable=True)
    metadata = Column(JSON, nullable=True)
    resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("idx_system_events_event_type", "event_type"),
        Index("idx_system_events_severity", "severity"),
        Index("idx_system_events_resolved", "resolved"),
        Index("idx_system_events_created_at", "created_at"),
    )


class SystemMetric(Base):
    """System performance metrics"""
    __tablename__ = "system_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    metric_type = Column(String(100), nullable=False)  # cpu_usage, memory_usage, response_time, error_rate, etc.
    value = Column(Float, nullable=False)
    unit = Column(String(50), nullable=True)  # percent, ms, count, etc.
    threshold_warning = Column(Float, nullable=True)
    threshold_critical = Column(Float, nullable=True)
    status = Column(String(20), default="normal")  # normal, warning, critical
    metadata = Column(JSON, nullable=True)
    recorded_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_system_metrics_metric_type", "metric_type"),
        Index("idx_system_metrics_recorded_at", "recorded_at"),
    )


class UserSuspension(Base):
    """Track user suspensions"""
    __tablename__ = "user_suspensions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    reason = Column(Text, nullable=False)
    suspended_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=False)
    suspended_at = Column(DateTime, default=datetime.utcnow)
    unsuspended_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="suspensions")
    suspended_by_admin = relationship("User", foreign_keys=[suspended_by], back_populates="suspensions_created")

    __table_args__ = (
        Index("idx_user_suspensions_user_id", "user_id"),
        Index("idx_user_suspensions_is_active", "is_active"),
    )
