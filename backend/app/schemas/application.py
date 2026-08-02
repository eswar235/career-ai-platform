"""
Pydantic schemas for application tracking
"""

from datetime import datetime, date
from typing import Optional
import uuid

from pydantic import BaseModel, Field


# ========== Application Schemas ==========

class JobApplicationBase(BaseModel):
    """Base application schema"""

    job_id: uuid.UUID = Field(..., description="Job ID")
    status: str = Field(default="applied", description="Application status")
    applied_via: Optional[str] = Field(None, description="Where application was submitted")
    cover_letter_id: Optional[uuid.UUID] = Field(None, description="Associated cover letter")
    resume_id: Optional[uuid.UUID] = Field(None, description="Associated resume")
    notes: Optional[str] = Field(None, description="Application notes")


class JobApplicationCreate(BaseModel):
    """Create application request"""

    job_id: uuid.UUID = Field(..., description="Job ID")
    applied_via: Optional[str] = Field(None, description="Where application was submitted")
    cover_letter_id: Optional[uuid.UUID] = Field(None, description="Associated cover letter")
    resume_id: Optional[uuid.UUID] = Field(None, description="Associated resume")
    notes: Optional[str] = Field(None, description="Application notes")


class JobApplicationUpdate(BaseModel):
    """Update application request"""

    status: Optional[str] = Field(None, description="New status")
    notes: Optional[str] = Field(None, description="Update notes")
    cover_letter_id: Optional[uuid.UUID] = Field(None, description="Update cover letter")
    resume_id: Optional[uuid.UUID] = Field(None, description="Update resume")


class JobApplicationResponse(BaseModel):
    """Application response"""

    id: uuid.UUID
    user_id: uuid.UUID
    job_id: uuid.UUID
    status: str
    application_date: datetime
    applied_via: Optional[str]
    cover_letter_id: Optional[uuid.UUID]
    resume_id: Optional[uuid.UUID]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class JobApplicationDetailResponse(JobApplicationResponse):
    """Detailed application with interviews and offer"""

    interviews: list["InterviewResponse"] = Field(default_factory=list)
    activities: list["ApplicationActivityResponse"] = Field(default_factory=list)
    offer: Optional["JobOfferResponse"] = None

    class Config:
        from_attributes = True


# ========== Interview Schemas ==========

class InterviewBase(BaseModel):
    """Base interview schema"""

    interview_type: Optional[str] = Field(None, description="Interview type")
    scheduled_date: Optional[datetime] = Field(None, description="Scheduled date/time")
    duration_minutes: Optional[int] = Field(None, description="Duration in minutes")
    interviewer_name: Optional[str] = Field(None, description="Interviewer name")
    interviewer_email: Optional[str] = Field(None, description="Interviewer email")
    meeting_link: Optional[str] = Field(None, description="Meeting link")
    preparation_notes: Optional[str] = Field(None, description="Preparation notes")


class InterviewCreate(InterviewBase):
    """Create interview request"""

    pass


class InterviewUpdate(BaseModel):
    """Update interview request"""

    interview_type: Optional[str] = Field(None)
    scheduled_date: Optional[datetime] = Field(None)
    duration_minutes: Optional[int] = Field(None)
    interviewer_name: Optional[str] = Field(None)
    interviewer_email: Optional[str] = Field(None)
    meeting_link: Optional[str] = Field(None)
    preparation_notes: Optional[str] = Field(None)
    status: Optional[str] = Field(None, description="Interview status")
    feedback: Optional[str] = Field(None, description="Feedback")
    interview_score: Optional[int] = Field(None, ge=1, le=10, description="Score 1-10")


class InterviewResponse(BaseModel):
    """Interview response"""

    id: uuid.UUID
    application_id: uuid.UUID
    interview_type: Optional[str]
    scheduled_date: Optional[datetime]
    duration_minutes: Optional[int]
    interviewer_name: Optional[str]
    interviewer_email: Optional[str]
    meeting_link: Optional[str]
    preparation_notes: Optional[str]
    feedback: Optional[str]
    interview_score: Optional[int]
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ========== Activity Schemas ==========

class ApplicationActivityResponse(BaseModel):
    """Activity log response"""

    id: uuid.UUID
    application_id: uuid.UUID
    activity_type: str
    description: Optional[str]
    previous_status: Optional[str]
    new_status: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ========== Offer Schemas ==========

class JobOfferBase(BaseModel):
    """Base offer schema"""

    salary: Optional[int] = Field(None, description="Annual salary")
    start_date: Optional[date] = Field(None, description="Start date")
    bonus: Optional[int] = Field(None, description="Bonus amount")
    benefits: Optional[str] = Field(None, description="Benefits description")
    offer_letter_url: Optional[str] = Field(None, description="Offer letter URL")
    offer_expiration_date: Optional[date] = Field(None, description="Expiration date")


class JobOfferCreate(JobOfferBase):
    """Create offer request"""

    pass


class JobOfferUpdate(BaseModel):
    """Update offer request"""

    status: Optional[str] = Field(None, description="Offer status")
    salary: Optional[int] = Field(None)
    start_date: Optional[date] = Field(None)
    bonus: Optional[int] = Field(None)
    benefits: Optional[str] = Field(None)
    offer_letter_url: Optional[str] = Field(None)
    offer_expiration_date: Optional[date] = Field(None)
    negotiation_notes: Optional[str] = Field(None, description="Negotiation notes")


class JobOfferResponse(BaseModel):
    """Offer response"""

    id: uuid.UUID
    application_id: uuid.UUID
    status: str
    salary: Optional[int]
    start_date: Optional[date]
    bonus: Optional[int]
    benefits: Optional[str]
    offer_letter_url: Optional[str]
    offer_expiration_date: Optional[date]
    negotiation_notes: Optional[str]
    accepted_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ========== Bulk Operations ==========

class BulkStatusUpdateRequest(BaseModel):
    """Bulk update status request"""

    application_ids: list[uuid.UUID] = Field(..., description="List of application IDs")
    new_status: str = Field(..., description="New status for all applications")
    notes: Optional[str] = Field(None, description="Notes for status change")


class BulkStatusUpdateResponse(BaseModel):
    """Bulk update response"""

    updated: int = Field(..., description="Number of applications updated")
    failed: int = Field(default=0, description="Number that failed")
    status: str


# ========== Dashboard/Analytics ==========

class ApplicationStats(BaseModel):
    """Application statistics"""

    total_applications: int
    status_breakdown: dict[str, int]  # {status: count}
    total_interviews: int
    completed_interviews: int
    offers_received: int
    offers_accepted: int
    rejection_rate: float
    average_time_to_interview: Optional[int]  # days
    average_time_to_offer: Optional[int]  # days


class ApplicationSummary(BaseModel):
    """Summary of application activity"""

    application_id: uuid.UUID
    job_title: str
    company: str
    status: str
    days_in_status: int
    next_step: Optional[str]
    interview_count: int
    last_activity: Optional[str]
    last_activity_date: Optional[datetime]
