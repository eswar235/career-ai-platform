"""
Pydantic schemas for profile-related API requests and responses
"""

from datetime import datetime, date
from typing import Optional
import uuid

from pydantic import BaseModel, Field, EmailStr


# Skill Schemas
class SkillCreate(BaseModel):
    skill_name: str = Field(..., min_length=1, max_length=100)
    proficiency_level: Optional[str] = Field(None, max_length=50)
    years_of_experience: Optional[int] = Field(None, ge=0)


class SkillUpdate(BaseModel):
    proficiency_level: Optional[str] = None
    years_of_experience: Optional[int] = None


class SkillResponse(BaseModel):
    id: uuid.UUID
    profile_id: uuid.UUID
    skill_name: str
    proficiency_level: Optional[str]
    years_of_experience: Optional[int]
    endorsed_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Experience Schemas
class ExperienceCreate(BaseModel):
    job_title: str = Field(..., min_length=1, max_length=255)
    company_name: str = Field(..., min_length=1, max_length=255)
    company_industry: Optional[str] = None
    employment_type: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    start_date: date
    end_date: Optional[date] = None
    currently_working: bool = False


class ExperienceUpdate(BaseModel):
    job_title: Optional[str] = None
    company_name: Optional[str] = None
    company_industry: Optional[str] = None
    employment_type: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    currently_working: Optional[bool] = None


class ExperienceResponse(BaseModel):
    id: uuid.UUID
    profile_id: uuid.UUID
    job_title: str
    company_name: str
    company_industry: Optional[str]
    employment_type: Optional[str]
    location: Optional[str]
    description: Optional[str]
    start_date: date
    end_date: Optional[date]
    currently_working: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Education Schemas
class EducationCreate(BaseModel):
    institution_name: str = Field(..., min_length=1, max_length=255)
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None
    grade: Optional[str] = None
    activities_societies: Optional[str] = None


class EducationUpdate(BaseModel):
    institution_name: Optional[str] = None
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None
    grade: Optional[str] = None
    activities_societies: Optional[str] = None


class EducationResponse(BaseModel):
    id: uuid.UUID
    profile_id: uuid.UUID
    institution_name: str
    degree: Optional[str]
    field_of_study: Optional[str]
    start_date: Optional[date]
    end_date: Optional[date]
    description: Optional[str]
    grade: Optional[str]
    activities_societies: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Project Schemas
class ProjectCreate(BaseModel):
    project_name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    skills_used: Optional[list[str]] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    project_url: Optional[str] = None
    image_url: Optional[str] = None


class ProjectUpdate(BaseModel):
    project_name: Optional[str] = None
    description: Optional[str] = None
    skills_used: Optional[list[str]] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    project_url: Optional[str] = None
    image_url: Optional[str] = None


class ProjectResponse(BaseModel):
    id: uuid.UUID
    profile_id: uuid.UUID
    project_name: str
    description: Optional[str]
    skills_used: Optional[list[str]]
    start_date: Optional[date]
    end_date: Optional[date]
    project_url: Optional[str]
    image_url: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Certification Schemas
class CertificationCreate(BaseModel):
    certification_name: str = Field(..., min_length=1, max_length=255)
    issuing_organization: Optional[str] = None
    issue_date: Optional[date] = None
    expiration_date: Optional[date] = None
    credential_id: Optional[str] = None
    credential_url: Optional[str] = None


class CertificationUpdate(BaseModel):
    certification_name: Optional[str] = None
    issuing_organization: Optional[str] = None
    issue_date: Optional[date] = None
    expiration_date: Optional[date] = None
    credential_id: Optional[str] = None
    credential_url: Optional[str] = None


class CertificationResponse(BaseModel):
    id: uuid.UUID
    profile_id: uuid.UUID
    certification_name: str
    issuing_organization: Optional[str]
    issue_date: Optional[date]
    expiration_date: Optional[date]
    credential_id: Optional[str]
    credential_url: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Profile Version Schemas
class ProfileVersionResponse(BaseModel):
    id: uuid.UUID
    profile_id: uuid.UUID
    version_number: int
    data: Optional[dict]
    changed_fields: Optional[list[str]]
    change_reason: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Profile Completion Tracking Schema
class ProfileCompletionTrackingResponse(BaseModel):
    id: uuid.UUID
    profile_id: uuid.UUID
    personal_info_complete: bool
    skills_added: bool
    experience_added: bool
    education_added: bool
    projects_added: bool
    certifications_added: bool
    profile_picture_added: bool
    professional_summary_added: bool
    last_updated: datetime

    class Config:
        from_attributes = True


# Main Profile Schemas
class UserProfileCreate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    headline: Optional[str] = None
    professional_summary: Optional[str] = None
    profile_picture_url: Optional[str] = None


class UserProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    headline: Optional[str] = None
    professional_summary: Optional[str] = None
    profile_picture_url: Optional[str] = None
    verified_by_user: Optional[bool] = None


class UserProfileResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    location: Optional[str]
    headline: Optional[str]
    professional_summary: Optional[str]
    profile_picture_url: Optional[str]
    completion_percentage: int
    verified_by_user: bool
    created_from_resume_id: Optional[uuid.UUID]
    created_at: datetime
    updated_at: datetime
    skills: list[SkillResponse] = []
    experiences: list[ExperienceResponse] = []
    education: list[EducationResponse] = []
    projects: list[ProjectResponse] = []
    certifications: list[CertificationResponse] = []
    completion_tracking: Optional[ProfileCompletionTrackingResponse] = None

    class Config:
        from_attributes = True


class UserProfileDetailResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    location: Optional[str]
    headline: Optional[str]
    professional_summary: Optional[str]
    profile_picture_url: Optional[str]
    completion_percentage: int
    verified_by_user: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
