"""
Analytics and dashboard models
"""

import uuid
from datetime import datetime, date
from typing import Optional

from sqlalchemy import Column, String, Integer, DateTime, Float, Date, ForeignKey, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class ApplicationStatistics(Base):
    """Aggregated application statistics for dashboard"""
    __tablename__ = "application_statistics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    total_submitted = Column(Integer, default=0)
    total_pending = Column(Integer, default=0)
    total_rejected = Column(Integer, default=0)
    total_interviews = Column(Integer, default=0)
    total_offers = Column(Integer, default=0)
    response_rate = Column(Float, nullable=True)  # % of applications that got response
    average_response_time_days = Column(Float, nullable=True)
    success_rate = Column(Float, nullable=True)  # % of applications that led to offer
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="application_statistics")

    __table_args__ = (
        Index("idx_app_stats_user_id", "user_id"),
    )


class ApplicationTrends(Base):
    """Time-series data for application trends"""
    __tablename__ = "application_trends"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    applications_submitted = Column(Integer, default=0)
    applications_reviewed = Column(Integer, default=0)
    interviews_scheduled = Column(Integer, default=0)
    rejections_received = Column(Integer, default=0)
    offers_received = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="application_trends")

    __table_args__ = (
        UniqueConstraint("user_id", "date", name="uq_user_date"),
        Index("idx_trends_user_id_date", "user_id", "date"),
    )


class JobAnalytics(Base):
    """Analytics data for individual job applications"""
    __tablename__ = "job_analytics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    application_count = Column(Integer, default=0)
    job_title = Column(String(255), nullable=True)
    company_name = Column(String(255), nullable=True)
    job_source = Column(String(100), nullable=True)
    experience_level = Column(String(50), nullable=True)
    applications_submitted = Column(Integer, default=1)
    date_applied = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="job_analytics")
    job = relationship("Job", back_populates="job_analytics")

    __table_args__ = (
        Index("idx_job_analytics_user_id", "user_id"),
        Index("idx_job_analytics_job_id", "job_id"),
    )


class RoleAnalytics(Base):
    """Analytics aggregated by job role/title"""
    __tablename__ = "role_analytics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    job_title = Column(String(255), nullable=False)
    application_count = Column(Integer, default=0)
    interview_count = Column(Integer, default=0)
    offer_count = Column(Integer, default=0)
    rejection_count = Column(Integer, default=0)
    last_applied = Column(Date, nullable=True)
    success_rate = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="role_analytics")

    __table_args__ = (
        UniqueConstraint("user_id", "job_title", name="uq_user_role"),
        Index("idx_role_analytics_user_id", "user_id"),
    )


class CompanyAnalytics(Base):
    """Analytics aggregated by company"""
    __tablename__ = "company_analytics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    company_name = Column(String(255), nullable=False)
    application_count = Column(Integer, default=0)
    interview_count = Column(Integer, default=0)
    offer_count = Column(Integer, default=0)
    rejection_count = Column(Integer, default=0)
    last_applied = Column(Date, nullable=True)
    success_rate = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="company_analytics")

    __table_args__ = (
        UniqueConstraint("user_id", "company_name", name="uq_user_company"),
        Index("idx_company_analytics_user_id", "user_id"),
    )


class SourceAnalytics(Base):
    """Analytics aggregated by job source"""
    __tablename__ = "source_analytics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    source_name = Column(String(100), nullable=False)
    application_count = Column(Integer, default=0)
    interview_count = Column(Integer, default=0)
    offer_count = Column(Integer, default=0)
    rejection_count = Column(Integer, default=0)
    success_rate = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="source_analytics")

    __table_args__ = (
        UniqueConstraint("user_id", "source_name", name="uq_user_source"),
        Index("idx_source_analytics_user_id", "user_id"),
    )
