"""
Browser automation models for job application automation
"""

from datetime import datetime
import uuid
from typing import Optional

from sqlalchemy import String, Integer, DateTime, ForeignKey, func, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class AutomationJob(Base):
    """Tracks browser automation jobs for job applications"""

    __tablename__ = "automation_jobs"

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

    job_url: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending", index=True)
    automation_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    browser_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, default="chrome")
    headless: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=True)
    max_retries: Mapped[int] = mapped_column(Integer(), nullable=False, default=3)
    current_retry: Mapped[int] = mapped_column(Integer(), nullable=False, default=0)
    error_message: Mapped[Optional[str]] = mapped_column(Text(), nullable=True)
    result: Mapped[Optional[str]] = mapped_column(Text(), nullable=True)

    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

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
    steps = relationship(
        "AutomationStep",
        back_populates="automation_job",
        cascade="all, delete-orphan",
        foreign_keys="AutomationStep.automation_job_id",
    )

    logs = relationship(
        "AutomationLog",
        back_populates="automation_job",
        cascade="all, delete-orphan",
        foreign_keys="AutomationLog.automation_job_id",
    )

    def __repr__(self) -> str:
        return f"<AutomationJob(user_id={self.user_id}, job_id={self.job_id}, status={self.status})>"


class AutomationStep(Base):
    """Individual steps in automation job"""

    __tablename__ = "automation_steps"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    automation_job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("automation_jobs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    step_order: Mapped[int] = mapped_column(Integer(), nullable=False)
    step_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    action_type: Mapped[str] = mapped_column(String(50), nullable=False)
    selector: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    value: Mapped[Optional[str]] = mapped_column(Text(), nullable=True)
    wait_time_ms: Mapped[Optional[int]] = mapped_column(Integer(), nullable=True)
    retry_on_fail: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=False)
    success: Mapped[Optional[bool]] = mapped_column(Boolean(), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text(), nullable=True)

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    automation_job = relationship("AutomationJob", back_populates="steps")

    def __repr__(self) -> str:
        return f"<AutomationStep(automation_job_id={self.automation_job_id}, action={self.action_type})>"


class AutomationLog(Base):
    """Logs for automation jobs"""

    __tablename__ = "automation_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    automation_job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("automation_jobs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    log_level: Mapped[str] = mapped_column(String(20), nullable=False)
    message: Mapped[Optional[str]] = mapped_column(Text(), nullable=True)
    screenshot_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    automation_job = relationship("AutomationJob", back_populates="logs")

    def __repr__(self) -> str:
        return f"<AutomationLog(automation_job_id={self.automation_job_id}, level={self.log_level})>"
