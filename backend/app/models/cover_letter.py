"""
Cover letter models for AI-powered cover letter generation
"""

from datetime import datetime
import uuid
from typing import Optional

from sqlalchemy import String, Integer, DateTime, ForeignKey, func, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class CoverLetter(Base):
    """AI-generated cover letters for job applications"""

    __tablename__ = "cover_letters"

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

    content: Mapped[str] = mapped_column(Text(), nullable=False)
    version_number: Mapped[int] = mapped_column(Integer(), nullable=False, default=1)
    is_draft: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=True)
    custom_edits: Mapped[Optional[str]] = mapped_column(Text(), nullable=True)
    ai_model: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
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
    exports = relationship(
        "LetterExport",
        back_populates="cover_letter",
        cascade="all, delete-orphan",
        foreign_keys="LetterExport.cover_letter_id",
    )

    def __repr__(self) -> str:
        return f"<CoverLetter(user_id={self.user_id}, job_id={self.job_id}, version={self.version_number})>"


class LetterTemplate(Base):
    """Reusable cover letter templates"""

    __tablename__ = "letter_templates"

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

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text(), nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=False)

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
        return f"<LetterTemplate(user_id={self.user_id}, name={self.name})>"


class LetterExport(Base):
    """Exported cover letters in various formats"""

    __tablename__ = "letter_exports"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    cover_letter_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cover_letters.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    format: Mapped[str] = mapped_column(String(20), nullable=False)  # pdf, docx, txt
    file_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    file_size: Mapped[Optional[int]] = mapped_column(Integer(), nullable=True)

    exported_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    cover_letter = relationship("CoverLetter", back_populates="exports")

    def __repr__(self) -> str:
        return f"<LetterExport(cover_letter_id={self.cover_letter_id}, format={self.format})>"
