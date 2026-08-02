"""
Resume model for storing uploaded resumes and metadata
"""

from datetime import datetime, timezone
import uuid

from sqlalchemy import String, Integer, DateTime, ForeignKey, func, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Resume(Base):
    """Resume model for storing user-uploaded resumes"""

    __tablename__ = "resumes"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    # Foreign key to User
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # File information
    filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # Original filename as uploaded by user
    original_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # File size in bytes
    file_size: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    # Storage path (local or cloud)
    storage_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    # File MIME type
    mime_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="application/pdf",
    )

    # Resume version/label (e.g., "v1", "v2", "latest")
    version: Mapped[str] = mapped_column(
        String(50),
        nullable=True,
    )

    # Whether this is the active/current resume
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    # Parsing status: pending, processing, completed, failed
    parsing_status: Mapped[str] = mapped_column(
        String(50),
        default="pending",
        nullable=False,
    )

    # Error message if parsing failed
    parsing_error: Mapped[str] = mapped_column(
        String(500),
        nullable=True,
    )

    # Timestamps
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    parsed_at: Mapped[datetime] = mapped_column(
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
        return f"<Resume(id={self.id}, user_id={self.user_id}, filename={self.original_filename})>"
