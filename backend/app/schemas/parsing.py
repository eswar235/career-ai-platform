"""
Pydantic schemas for parsing-related requests and responses
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class SkillData(BaseModel):
    """Schema for skill data"""

    name: str = Field(..., description="Skill name")
    proficiency: Optional[str] = Field(
        None, description="Beginner, Intermediate, Advanced, Expert"
    )
    years: Optional[int] = Field(None, description="Years of experience")


class ExperienceData(BaseModel):
    """Schema for work experience"""

    title: str = Field(..., description="Job title")
    company: str = Field(..., description="Company name")
    start_date: Optional[str] = Field(None, description="Start date")
    end_date: Optional[str] = Field(None, description="End date or 'Present'")
    description: Optional[str] = Field(None, description="Job description")


class EducationData(BaseModel):
    """Schema for education"""

    degree: str = Field(..., description="Degree (e.g., Bachelor, Master)")
    institution: str = Field(..., description="School/University name")
    year: Optional[int] = Field(None, description="Graduation year")
    field: Optional[str] = Field(None, description="Field of study")


class CertificationData(BaseModel):
    """Schema for certification"""

    name: str = Field(..., description="Certification name")
    issuer: str = Field(..., description="Issuing organization")
    year: Optional[int] = Field(None, description="Year obtained")


class ParsedResumeResponse(BaseModel):
    """Schema for parsed resume response"""

    id: UUID = Field(..., description="ParsedResume ID")
    resume_id: UUID = Field(..., description="Source Resume ID")
    user_id: UUID = Field(..., description="User ID")

    # Personal Information
    full_name: Optional[str] = Field(None, description="Full name")
    email: Optional[str] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    location: Optional[str] = Field(None, description="Location")
    summary: Optional[str] = Field(None, description="Professional summary")

    # Structured Data
    skills: list[SkillData] = Field(default_factory=list, description="List of skills")
    experience: list[ExperienceData] = Field(
        default_factory=list, description="Work experience"
    )
    education: list[EducationData] = Field(
        default_factory=list, description="Education"
    )
    certifications: list[CertificationData] = Field(
        default_factory=list, description="Certifications"
    )

    # Metadata
    confidence_score: Optional[int] = Field(
        None, description="Confidence score 0-100"
    )
    is_confirmed: bool = Field(False, description="User confirmed parsing")
    created_at: datetime = Field(..., description="Created timestamp")
    confirmed_at: Optional[datetime] = Field(None, description="Confirmed timestamp")

    class Config:
        from_attributes = True


class ParsedResumeUpdate(BaseModel):
    """Schema for updating parsed resume"""

    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    summary: Optional[str] = None
    skills: Optional[list[SkillData]] = None
    experience: Optional[list[ExperienceData]] = None
    education: Optional[list[EducationData]] = None
    certifications: Optional[list[CertificationData]] = None


class ParsedResumeConfirmRequest(BaseModel):
    """Schema for confirming parsed resume"""

    parsed_resume_id: UUID = Field(..., description="ParsedResume ID to confirm")


class ParseResumeResponse(BaseModel):
    """Schema for parse resume endpoint response"""

    parsed_resume_id: UUID = Field(..., description="ParsedResume ID")
    resume_id: UUID = Field(..., description="Source Resume ID")
    full_name: Optional[str] = Field(None, description="Extracted name")
    email: Optional[str] = Field(None, description="Extracted email")
    confidence_score: int = Field(..., description="Confidence score 0-100")
    message: str = Field(..., description="Status message")

    class Config:
        from_attributes = True
