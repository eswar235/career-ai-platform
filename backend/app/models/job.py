"""
Job search models for storing jobs, saved jobs, search history, and applications
"""

from datetime import datetime
import uuid
from typing import Optional

from sqlalchemy import String, Integer, DateTime, ForeignKey, func, Boolean, Date, Text, JSON, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Job(Base):
    """Job posting model"""

    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    company_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)

    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    job_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    salary_min: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    salary_max: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    salary_currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)

    description: Mapped[Optional[str]] = mapped_column(Text(), nullable=True)
    requirements: Mapped[Optional[str]] = mapped_column(Text(), nullable=True)
    benefits: Mapped[Optional[str]] = mapped_column(Text(), nullable=True)

    industry: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    experience_level: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    skills_required: Mapped[Optional[list]] = mapped_column(ARRAY(String()), nullable=True)

    posted_date: Mapped[datetime] = mapped_column(
        Date(),
        nullable=False,
        index=True,
    )

    application_deadline: Mapped[Optional[datetime]] = mapped_column(Date(), nullable=True)

    source: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    source_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    saved_by = relationship(
        "SavedJob",
        back_populates="job",
        cascade="all, delete-orphan",
        foreign_keys="SavedJob.job_id",
    )
    applications = relationship(
        "JobApplication",
        back_populates="job",
        cascade="all, delete-orphan",
        foreign_keys="JobApplication.job_id",
    )
    alert_matches = relationship(
        "AlertJobMatch",
        back_populates="job",
        cascade="all, delete-orphan",
        foreign_keys="AlertJobMatch.job_id",
    )
    job_analytics = relationship(
        "JobAnalytics",
        back_populates="job",
        cascade="all, delete-orphan",
        foreign_keys="JobAnalytics.job_id",
    )

    def __repr__(self) -> str:
        return f"<Job(id={self.id}, title={self.title}, company={self.company_name})>"


class SavedJob(Base):
    """Saved/bookmarked jobs"""

    __tablename__ = "saved_jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    saved_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    notes: Mapped[Optional[str]] = mapped_column(Text(), nullable=True)

    # Relationships
    job = relationship("Job", back_populates="saved_by")

    def __repr__(self) -> str:
        return f"<SavedJob(user_id={self.user_id}, job_id={self.job_id})>"


class JobSearchHistory(Base):
    """Track user job searches"""

    __tablename__ = "job_search_history"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    search_query: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    filters_applied: Mapped[Optional[dict]] = mapped_column(JSON(), nullable=True)
    results_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    searched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    def __repr__(self) -> str:
        return f"<JobSearchHistory(user_id={self.user_id}, query={self.search_query})>"


class JobApplication(Base):
    """Track job applications"""

    __tablename__ = "job_applications"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="applied",
        nullable=False,
        index=True,
    )

    applied_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    notes: Mapped[Optional[str]] = mapped_column(Text(), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    job = relationship("Job", back_populates="applications")

    def __repr__(self) -> str:
        return f"<JobApplication(user_id={self.user_id}, job_id={self.job_id}, status={self.status})>"
