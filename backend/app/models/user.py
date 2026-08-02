"""
User model for authentication and profile management
"""

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

import uuid

from app.core.database import Base


class User(Base):
    """User model for authentication and basic profile"""

    __tablename__ = "users"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    # Authentication fields
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # Profile fields
    full_name: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
    )

    # Email verification
    email_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # Account status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    # Timestamps
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
    last_login: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Admin fields (added in Phase 13)
    from sqlalchemy.dialects.postgresql import JSON as JSON_TYPE
    is_admin: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    is_superuser: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    permissions: Mapped[dict] = mapped_column(
        JSON_TYPE,
        nullable=True,
    )

    # Relationships for notifications (added in Phase 11)
    job_alert = relationship("JobAlert", back_populates="user", uselist=False)
    notifications = relationship("Notification", back_populates="user")
    email_notifications = relationship("EmailNotification", back_populates="user")
    notification_preferences = relationship("NotificationPreferences", back_populates="user", uselist=False)

    # Relationships for analytics (added in Phase 12)
    application_statistics = relationship("ApplicationStatistics", back_populates="user", uselist=False)
    application_trends = relationship("ApplicationTrends", back_populates="user")
    job_analytics = relationship("JobAnalytics", back_populates="user")
    role_analytics = relationship("RoleAnalytics", back_populates="user")
    company_analytics = relationship("CompanyAnalytics", back_populates="user")
    source_analytics = relationship("SourceAnalytics", back_populates="user")

    # Relationships for admin (added in Phase 13)
    audit_logs_as_user = relationship("AuditLog", foreign_keys="AuditLog.user_id", back_populates="user")
    audit_logs_as_admin = relationship("AuditLog", foreign_keys="AuditLog.admin_id", back_populates="admin")
    suspensions = relationship("UserSuspension", foreign_keys="UserSuspension.user_id", back_populates="user")
    suspensions_created = relationship("UserSuspension", foreign_keys="UserSuspension.suspended_by", back_populates="suspended_by_admin")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email})>"

    def update_last_login(self) -> None:
        """Update last login timestamp"""
        self.last_login = datetime.now(timezone.utc)

