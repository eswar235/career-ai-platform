"""
Notification and alert models
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String, Boolean, DateTime, Float, Integer, Text, ForeignKey, Time, JSON, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class JobAlert(Base):
    """Job alert model for user preferences"""
    __tablename__ = "job_alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    keywords = Column(Text, nullable=True)
    locations = Column(JSON, nullable=True)
    job_titles = Column(JSON, nullable=True)
    experience_levels = Column(JSON, nullable=True)
    salary_min = Column(Integer, nullable=True)
    salary_max = Column(Integer, nullable=True)
    min_match_score = Column(Float, default=60)
    notification_frequency = Column(String(50), default="daily")
    preferred_time = Column(Time, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="job_alert")
    matched_jobs = relationship("AlertJobMatch", back_populates="job_alert", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_job_alerts_user_id", "user_id"),
        Index("idx_job_alerts_is_active", "is_active"),
    )


class Notification(Base):
    """In-app notification model"""
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    notification_type = Column(String(50), nullable=False)  # job_alert, application_update, interview_reminder, etc.
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    related_entity_type = Column(String(50), nullable=True)  # job, application, interview, etc.
    related_entity_id = Column(UUID(as_uuid=True), nullable=True)
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="notifications")

    __table_args__ = (
        Index("idx_notifications_user_id", "user_id"),
        Index("idx_notifications_is_read", "is_read"),
        Index("idx_notifications_created_at", "created_at"),
    )


class EmailNotification(Base):
    """Email notification model for tracking sent emails"""
    __tablename__ = "email_notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    email_address = Column(String(255), nullable=False)
    notification_type = Column(String(50), nullable=False)  # job_alert, application_update, etc.
    subject = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    status = Column(String(50), default="pending")  # pending, sent, failed, bounced
    sent_at = Column(DateTime, nullable=True)
    delivery_error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="email_notifications")

    __table_args__ = (
        Index("idx_email_notifications_user_id", "user_id"),
        Index("idx_email_notifications_status", "status"),
    )


class AlertJobMatch(Base):
    """Track which jobs matched user alerts"""
    __tablename__ = "alert_job_matches"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    alert_id = Column(UUID(as_uuid=True), ForeignKey("job_alerts.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    match_score = Column(Float, nullable=True)
    notification_sent = Column(Boolean, default=False)
    user_dismissed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    job_alert = relationship("JobAlert", back_populates="matched_jobs")
    job = relationship("Job", back_populates="alert_matches")

    __table_args__ = (
        UniqueConstraint("alert_id", "job_id", name="uq_alert_job"),
        Index("idx_alert_job_matches_alert_id", "alert_id"),
        Index("idx_alert_job_matches_job_id", "job_id"),
        Index("idx_alert_job_matches_notification_sent", "notification_sent"),
    )


class NotificationPreferences(Base):
    """User notification preferences"""
    __tablename__ = "notification_preferences"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    job_alerts_enabled = Column(Boolean, default=True)
    application_updates_enabled = Column(Boolean, default=True)
    interview_reminders_enabled = Column(Boolean, default=True)
    daily_digest_enabled = Column(Boolean, default=False)
    digest_time = Column(Time, nullable=True)
    email_notifications_enabled = Column(Boolean, default=True)
    in_app_notifications_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="notification_preferences")

    __table_args__ = (
        Index("idx_notification_preferences_user_id", "user_id"),
    )
