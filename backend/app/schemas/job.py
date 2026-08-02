"""
Pydantic schemas for job search-related API requests and responses
"""

from datetime import datetime, date
from typing import Optional
import uuid

from pydantic import BaseModel, Field


# Job Schemas
class JobCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    company_name: str = Field(..., min_length=1, max_length=255)
    company_id: Optional[uuid.UUID] = None
    location: Optional[str] = None
    job_type: Optional[str] = None
    salary_min: Optional[int] = Field(None, ge=0)
    salary_max: Optional[int] = Field(None, ge=0)
    salary_currency: Optional[str] = "USD"
    description: Optional[str] = None
    requirements: Optional[str] = None
    benefits: Optional[str] = None
    industry: Optional[str] = None
    experience_level: Optional[str] = None
    skills_required: Optional[list[str]] = None
    posted_date: date
    application_deadline: Optional[date] = None
    source: Optional[str] = None
    source_url: Optional[str] = None


class JobUpdate(BaseModel):
    title: Optional[str] = None
    company_name: Optional[str] = None
    location: Optional[str] = None
    job_type: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    benefits: Optional[str] = None
    industry: Optional[str] = None
    experience_level: Optional[str] = None
    skills_required: Optional[list[str]] = None
    application_deadline: Optional[date] = None
    source_url: Optional[str] = None
    is_active: Optional[bool] = None


class JobResponse(BaseModel):
    id: uuid.UUID
    title: str
    company_name: str
    company_id: Optional[uuid.UUID]
    location: Optional[str]
    job_type: Optional[str]
    salary_min: Optional[int]
    salary_max: Optional[int]
    salary_currency: str
    description: Optional[str]
    requirements: Optional[str]
    benefits: Optional[str]
    industry: Optional[str]
    experience_level: Optional[str]
    skills_required: Optional[list[str]]
    posted_date: date
    application_deadline: Optional[date]
    source: Optional[str]
    source_url: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Saved Job Schemas
class SavedJobCreate(BaseModel):
    job_id: uuid.UUID
    notes: Optional[str] = None


class SavedJobResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    job_id: uuid.UUID
    saved_at: datetime
    notes: Optional[str]
    job: Optional[JobResponse] = None

    class Config:
        from_attributes = True


# Job Search Filters
class JobSearchFilters(BaseModel):
    keyword: Optional[str] = None
    location: Optional[str] = None
    job_type: Optional[str] = None
    experience_level: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    industry: Optional[str] = None
    company_name: Optional[str] = None
    posted_after: Optional[date] = None
    skip: int = Field(0, ge=0)
    limit: int = Field(20, ge=1, le=100)
    sort_by: Optional[str] = "posted_date"  # posted_date, relevance, salary


# Job Search History Schemas
class JobSearchHistoryResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    search_query: Optional[str]
    filters_applied: Optional[dict]
    results_count: Optional[int]
    searched_at: datetime

    class Config:
        from_attributes = True


# Job Application Schemas
class JobApplicationCreate(BaseModel):
    job_id: uuid.UUID
    notes: Optional[str] = None


class JobApplicationUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None


class JobApplicationResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    job_id: uuid.UUID
    status: str
    applied_date: datetime
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    job: Optional[JobResponse] = None

    class Config:
        from_attributes = True


# Search Results
class JobSearchResults(BaseModel):
    total: int
    skip: int
    limit: int
    jobs: list[JobResponse]
    
    class Config:
        from_attributes = True
