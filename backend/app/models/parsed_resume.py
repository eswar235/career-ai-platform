"""
ParsedResume model for storing extracted resume data
"""

from datetime import datetime, timezone
import uuid
from typing import Optional

from sqlalchemy import String, Integer, DateTime, ForeignKey, func, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ParsedResume(Base):
    """Model for storing parsed resume data extracted by AI"""

    __tablename__ = "parsed_resumes"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    # Foreign key to Resume
    resume_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("resumes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        unique=True,  # One parsing per resume
    )

    # Foreign key to User
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Personal Information
    full_name: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
    )

    phone: Mapped[str] = mapped_column(
        String(20),
        nullable=True,
    )

    location: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
    )

    # Professional Summary
    summary: Mapped[str] = mapped_column(
        Text,
        nullable=True,
    )

    # Skills (stored as JSON array)
    # Format: [{"name": "Python", "proficiency": "Expert", "years": 5}, ...]
    skills: Mapped[dict] = mapped_column(
        JSON,
        nullable=True,
        default=list,
    )

    # Experience (stored as JSON array)
    # Format: [{"title": "...", "company": "...", "duration": "...", "description": "..."}, ...]
    experience: Mapped[dict] = mapped_column(
        JSON,
        nullable=True,
        default=list,
    )

    # Education (stored as JSON array)
    # Format: [{"degree": "...", "institution": "...", "year": "...", "field": "..."}, ...]
    education: Mapped[dict] = mapped_column(
        JSON,
        nullable=True,
        default=list,
    )

    # Certifications (stored as JSON array)
    certifications: Mapped[dict] = mapped_column(
        JSON,
        nullable=True,
        default=list,
    )

    # Raw extracted text from PDF
    raw_text: Mapped[str] = mapped_column(
        Text,
        nullable=True,
    )

    # Parsing confidence score (0-100)
    confidence_score: Mapped[int] = mapped_column(
        Integer,
        nullable=True,
    )

    # Extraction quality notes
    quality_notes: Mapped[str] = mapped_column(
        Text,
        nullable=True,
    )

    # Whether user has reviewed and confirmed
    is_confirmed: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    confirmed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<ParsedResume(id={self.id}, resume_id={self.resume_id}, name={self.full_name})>"

    def confirm(self) -> None:
        """Mark parsing as confirmed by user"""
        self.is_confirmed = True
        self.confirmed_at = datetime.now(timezone.utc)
