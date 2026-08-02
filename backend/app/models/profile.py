"""
User profile models for storing user information, skills, experience, education, projects, certifications, and version history
"""

from datetime import datetime
import uuid
from typing import Optional

from sqlalchemy import String, Integer, DateTime, ForeignKey, func, Boolean, Date, Text, JSON, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class UserProfile(Base):
    """Main user profile table"""

    __tablename__ = "user_profiles"

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

    first_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    headline: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    professional_summary: Mapped[Optional[str]] = mapped_column(Text(), nullable=True)
    profile_picture_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    completion_percentage: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    verified_by_user: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_from_resume_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("resumes.id", ondelete="SET NULL"),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    skills = relationship(
        "ProfileSkill",
        back_populates="profile",
        cascade="all, delete-orphan",
        foreign_keys="ProfileSkill.profile_id",
    )
    experiences = relationship(
        "ProfileExperience",
        back_populates="profile",
        cascade="all, delete-orphan",
        foreign_keys="ProfileExperience.profile_id",
    )
    education = relationship(
        "ProfileEducation",
        back_populates="profile",
        cascade="all, delete-orphan",
        foreign_keys="ProfileEducation.profile_id",
    )
    projects = relationship(
        "ProfileProject",
        back_populates="profile",
        cascade="all, delete-orphan",
        foreign_keys="ProfileProject.profile_id",
    )
    certifications = relationship(
        "ProfileCertification",
        back_populates="profile",
        cascade="all, delete-orphan",
        foreign_keys="ProfileCertification.profile_id",
    )
    versions = relationship(
        "ProfileVersion",
        back_populates="profile",
        cascade="all, delete-orphan",
        foreign_keys="ProfileVersion.profile_id",
    )
    completion_tracking = relationship(
        "ProfileCompletionTracking",
        back_populates="profile",
        uselist=False,
        cascade="all, delete-orphan",
        foreign_keys="ProfileCompletionTracking.profile_id",
    )

    def __repr__(self) -> str:
        return f"<UserProfile(id={self.id}, user_id={self.user_id}, email={self.email})>"


class ProfileSkill(Base):
    """Skills associated with a user profile"""

    __tablename__ = "profile_skills"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    skill_name: Mapped[str] = mapped_column(String(100), nullable=False)
    proficiency_level: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    years_of_experience: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    endorsed_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

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

    profile = relationship("UserProfile", back_populates="skills")

    __table_args__ = (
        # Unique constraint on profile_id and skill_name (case-insensitive)
    )

    def __repr__(self) -> str:
        return f"<ProfileSkill(id={self.id}, skill_name={self.skill_name})>"


class ProfileExperience(Base):
    """Work experience for a user profile"""

    __tablename__ = "profile_experiences"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    job_title: Mapped[str] = mapped_column(String(255), nullable=False)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    company_industry: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    employment_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text(), nullable=True)

    start_date: Mapped[datetime] = mapped_column(Date(), nullable=False)
    end_date: Mapped[Optional[datetime]] = mapped_column(Date(), nullable=True)
    currently_working: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

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

    profile = relationship("UserProfile", back_populates="experiences")

    def __repr__(self) -> str:
        return f"<ProfileExperience(id={self.id}, job_title={self.job_title})>"


class ProfileEducation(Base):
    """Education history for a user profile"""

    __tablename__ = "profile_education"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    institution_name: Mapped[str] = mapped_column(String(255), nullable=False)
    degree: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    field_of_study: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    start_date: Mapped[Optional[datetime]] = mapped_column(Date(), nullable=True)
    end_date: Mapped[Optional[datetime]] = mapped_column(Date(), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text(), nullable=True)
    grade: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    activities_societies: Mapped[Optional[str]] = mapped_column(Text(), nullable=True)

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

    profile = relationship("UserProfile", back_populates="education")

    def __repr__(self) -> str:
        return f"<ProfileEducation(id={self.id}, institution={self.institution_name})>"


class ProfileProject(Base):
    """Portfolio projects for a user profile"""

    __tablename__ = "profile_projects"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    project_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text(), nullable=True)
    skills_used: Mapped[Optional[list]] = mapped_column(ARRAY(String()), nullable=True)
    start_date: Mapped[Optional[datetime]] = mapped_column(Date(), nullable=True)
    end_date: Mapped[Optional[datetime]] = mapped_column(Date(), nullable=True)
    project_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

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

    profile = relationship("UserProfile", back_populates="projects")

    def __repr__(self) -> str:
        return f"<ProfileProject(id={self.id}, project_name={self.project_name})>"


class ProfileCertification(Base):
    """Certifications for a user profile"""

    __tablename__ = "profile_certifications"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    certification_name: Mapped[str] = mapped_column(String(255), nullable=False)
    issuing_organization: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    issue_date: Mapped[Optional[datetime]] = mapped_column(Date(), nullable=True)
    expiration_date: Mapped[Optional[datetime]] = mapped_column(Date(), nullable=True)
    credential_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    credential_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

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

    profile = relationship("UserProfile", back_populates="certifications")

    def __repr__(self) -> str:
        return f"<ProfileCertification(id={self.id}, certification={self.certification_name})>"


class ProfileVersion(Base):
    """Version history for profile changes"""

    __tablename__ = "profile_versions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    data: Mapped[Optional[dict]] = mapped_column(JSON(), nullable=True)
    changed_fields: Mapped[Optional[list]] = mapped_column(ARRAY(String()), nullable=True)
    change_reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    profile = relationship("UserProfile", back_populates="versions")

    def __repr__(self) -> str:
        return f"<ProfileVersion(id={self.id}, version={self.version_number})>"


class ProfileCompletionTracking(Base):
    """Track profile completion status"""

    __tablename__ = "profile_completion_tracking"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user_profiles.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    personal_info_complete: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    skills_added: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    experience_added: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    education_added: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    projects_added: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    certifications_added: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    profile_picture_added: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    professional_summary_added: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    last_updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    profile = relationship("UserProfile", back_populates="completion_tracking", uselist=False)

    def __repr__(self) -> str:
        return f"<ProfileCompletionTracking(profile_id={self.profile_id})>"
