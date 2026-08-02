"""
Resume optimization models for tracking optimizations and tailored versions
"""

from datetime import datetime
import uuid
from typing import Optional

from sqlalchemy import String, Integer, DateTime, ForeignKey, func, Text, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ResumeOptimization(Base):
    """Resume optimization analysis and scores"""

    __tablename__ = "resume_optimizations"

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
        unique=True,
        index=True,
    )

    original_content: Mapped[str] = mapped_column(Text(), nullable=False)
    optimized_content: Mapped[Optional[str]] = mapped_column(Text(), nullable=True)

    # Scoring
    ats_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    keyword_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    formatting_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    readability_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    overall_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

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
    suggestions = relationship(
        "OptimizationSuggestion",
        back_populates="optimization",
        cascade="all, delete-orphan",
        foreign_keys="OptimizationSuggestion.optimization_id",
    )

    def __repr__(self) -> str:
        return f"<ResumeOptimization(user_id={self.user_id}, score={self.overall_score})>"


class TailoredResume(Base):
    """Job-specific tailored resume versions"""

    __tablename__ = "tailored_resumes"

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

    tailored_content: Mapped[str] = mapped_column(Text(), nullable=False)

    # Scoring
    match_keywords: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    ats_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    keyword_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Recommendations for this tailoring
    recommendations: Mapped[Optional[list]] = mapped_column(ARRAY(String()), nullable=True)

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

    def __repr__(self) -> str:
        return f"<TailoredResume(user_id={self.user_id}, job_id={self.job_id})>"


class OptimizationSuggestion(Base):
    """Suggestions for resume optimization"""

    __tablename__ = "optimization_suggestions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    optimization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("resume_optimizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    category: Mapped[str] = mapped_column(String(50), nullable=False)
    suggestion: Mapped[str] = mapped_column(Text(), nullable=False)
    priority: Mapped[str] = mapped_column(String(20), nullable=False)
    impact_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    optimization = relationship("ResumeOptimization", back_populates="suggestions")

    def __repr__(self) -> str:
        return f"<OptimizationSuggestion(category={self.category}, priority={self.priority})>"
