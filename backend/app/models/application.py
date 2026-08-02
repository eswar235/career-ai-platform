"""
Job application tracking models
"""

from datetime import datetime, date
import uuid
from typing import Optional

from sqlalchemy import String, Integer, DateTime, ForeignKey, func, Text, Date, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


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

    status: Mapped[str] = mapped_column(String(50), nullable=False, default="applied", index=True)
    application_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    applied_via: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    cover_letter_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cover_letters.id", ondelete="SET NULL"),
        nullable=True,
    )

    resume_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("resumes.id", ondelete="SET NULL"),
        nullable=True,
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
    interviews = relationship(
        "Interview",
        back_populates="application",
        cascade="all, delete-orphan",
        foreign_keys="Interview.application_id",
    )

    activities = relationship(
        "ApplicationActivity",
        back_populates="application",
        cascade="all, delete-orphan",
        foreign_keys="ApplicationActivity.application_id",
    )

    offer = relationship(
        "JobOffer",
        back_populates="application",
        cascade="all, delete-orphan",
        uselist=False,
        foreign_keys="JobOffer.application_id",
    )

    def __repr__(self) -> str:
        return f"<JobApplication(user_id={self.user_id}, job_id={self.job_id}, status={self.status})>"


class Interview(Base):
    """Interview information for applications"""

    __tablename__ = "interviews"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    application_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("job_applications.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    interview_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    scheduled_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    duration_minutes: Mapped[Optional[int]] = mapped_column(Integer(), nullable=True)
    interviewer_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    interviewer_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    meeting_link: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    preparation_notes: Mapped[Optional[str]] = mapped_column(Text(), nullable=True)
    feedback: Mapped[Optional[str]] = mapped_column(Text(), nullable=True)
    interview_score: Mapped[Optional[int]] = mapped_column(Integer(), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="scheduled")

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
    application = relationship("JobApplication", back_populates="interviews")

    def __repr__(self) -> str:
        return f"<Interview(application_id={self.application_id}, type={self.interview_type})>"


class ApplicationActivity(Base):
    """Activity log for application events"""

    __tablename__ = "application_activities"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    application_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("job_applications.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    activity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text(), nullable=True)
    previous_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    new_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    application = relationship("JobApplication", back_populates="activities")

    def __repr__(self) -> str:
        return f"<ApplicationActivity(application_id={self.application_id}, type={self.activity_type})>"


class JobOffer(Base):
    """Job offer tracking"""

    __tablename__ = "job_offers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    application_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("job_applications.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        unique=True,
    )

    status: Mapped[str] = mapped_column(String(50), nullable=False, default="received")
    salary: Mapped[Optional[int]] = mapped_column(Integer(), nullable=True)
    start_date: Mapped[Optional[date]] = mapped_column(Date(), nullable=True)
    bonus: Mapped[Optional[int]] = mapped_column(Integer(), nullable=True)
    benefits: Mapped[Optional[str]] = mapped_column(Text(), nullable=True)
    offer_letter_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    offer_expiration_date: Mapped[Optional[date]] = mapped_column(Date(), nullable=True)
    negotiation_notes: Mapped[Optional[str]] = mapped_column(Text(), nullable=True)
    accepted_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

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
    application = relationship("JobApplication", back_populates="offer")

    def __repr__(self) -> str:
        return f"<JobOffer(application_id={self.application_id}, status={self.status})>"
