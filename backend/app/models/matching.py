"""
Job matching models for embeddings and similarity scoring
"""

from datetime import datetime
import uuid
from typing import Optional

from sqlalchemy import String, Integer, DateTime, ForeignKey, func, Boolean, Date, Text, JSON, ARRAY, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ResumeEmbedding(Base):
    """Resume embeddings for similarity matching"""

    __tablename__ = "resume_embeddings"

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

    content: Mapped[str] = mapped_column(Text(), nullable=False)
    
    # Store embedding as JSON array (compatible with non-pgvector setups)
    embedding: Mapped[Optional[dict]] = mapped_column(JSON(), nullable=True)
    
    skills_extracted: Mapped[Optional[list]] = mapped_column(ARRAY(String()), nullable=True)
    experience_summary: Mapped[Optional[str]] = mapped_column(Text(), nullable=True)

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
        return f"<ResumeEmbedding(user_id={self.user_id})>"


class JobEmbedding(Base):
    """Job embeddings for similarity matching"""

    __tablename__ = "job_embeddings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    content: Mapped[str] = mapped_column(Text(), nullable=False)
    
    # Store embedding as JSON array (compatible with non-pgvector setups)
    embedding: Mapped[Optional[dict]] = mapped_column(JSON(), nullable=True)
    
    skills_required_normalized: Mapped[Optional[list]] = mapped_column(ARRAY(String()), nullable=True)

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
        return f"<JobEmbedding(job_id={self.job_id})>"


class JobMatch(Base):
    """Pre-computed job matches with scores and recommendations"""

    __tablename__ = "job_matches"

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

    # Match score 0-100%
    match_percentage: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    
    # Detailed match score 0.0-1.0
    match_score: Mapped[float] = mapped_column(Numeric(precision=5, scale=4), nullable=False)

    # Skill matching details
    skills_match: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    skills_missing: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Analysis arrays
    strengths: Mapped[Optional[list]] = mapped_column(ARRAY(String()), nullable=True)
    gaps: Mapped[Optional[list]] = mapped_column(ARRAY(String()), nullable=True)
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
        return f"<JobMatch(user_id={self.user_id}, job_id={self.job_id}, match={self.match_percentage}%)>"
