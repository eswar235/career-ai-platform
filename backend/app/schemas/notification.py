"""
Notification and alert schemas
"""

from datetime import datetime, time
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, EmailStr


# Job Alert Schemas
class JobAlertCreate(BaseModel):
    """Create job alert request"""
    keywords: Optional[str] = None
    locations: Optional[List[str]] = None
    job_titles: Optional[List[str]] = None
    experience_levels: Optional[List[str]] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    min_match_score: Optional[float] = Field(default=60, ge=0, le=100)
    notification_frequency: str = Field(default="daily")
    preferred_time: Optional[time] = None


class JobAlertUpdate(BaseModel):
    """Update job alert request"""
    keywords: Optional[str] = None
    locations: Optional[List[str]] = None
    job_titles: Optional[List[str]] = None
    experience_levels: Optional[List[str]] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    min_match_score: Optional[float] = Field(default=None, ge=0, le=100)
    notification_frequency: Optional[str] = None
    preferred_time: Optional[time] = None
    is_active: Optional[bool] = None


class JobAlertResponse(BaseModel):
    """Job alert response"""
    id: UUID
    user_id: UUID
    keywords: Optional[str] = None
    locations: Optional[List[str]] = None
    job_titles: Optional[List[str]] = None
    experience_levels: Optional[List[str]] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    min_match_score: float
    notification_frequency: str
    preferred_time: Optional[time] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Notification Schemas
class NotificationResponse(BaseModel):
    """Notification response"""
    id: UUID
    user_id: UUID
    notification_type: str
    title: str
    message: str
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[UUID] = None
    is_read: bool
    read_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NotificationMarkReadRequest(BaseModel):
    """Mark notification as read request"""
    is_read: bool = True


# Email Notification Schemas
class EmailNotificationResponse(BaseModel):
    """Email notification response"""
    id: UUID
    user_id: UUID
    email_address: str
    notification_type: str
    subject: str
    body: str
    status: str
    sent_at: Optional[datetime] = None
    delivery_error: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Alert Job Match Schemas
class AlertJobMatchResponse(BaseModel):
    """Alert job match response"""
    id: UUID
    alert_id: UUID
    job_id: UUID
    match_score: Optional[float] = None
    notification_sent: bool
    user_dismissed: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Notification Preferences Schemas
class NotificationPreferencesUpdate(BaseModel):
    """Update notification preferences request"""
    job_alerts_enabled: Optional[bool] = None
    application_updates_enabled: Optional[bool] = None
    interview_reminders_enabled: Optional[bool] = None
    daily_digest_enabled: Optional[bool] = None
    digest_time: Optional[time] = None
    email_notifications_enabled: Optional[bool] = None
    in_app_notifications_enabled: Optional[bool] = None


class NotificationPreferencesResponse(BaseModel):
    """Notification preferences response"""
    id: UUID
    user_id: UUID
    job_alerts_enabled: bool
    application_updates_enabled: bool
    interview_reminders_enabled: bool
    daily_digest_enabled: bool
    digest_time: Optional[time] = None
    email_notifications_enabled: bool
    in_app_notifications_enabled: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Notification Summary Schemas
class NotificationsSummaryResponse(BaseModel):
    """Notifications summary response"""
    total_unread: int
    total_notifications: int
    job_alerts_count: int
    application_updates_count: int
    interview_reminders_count: int
    notifications: List[NotificationResponse] = []


class AlertMatchesResponse(BaseModel):
    """Alert matches response"""
    total_matches: int
    new_matches: int
    matches: List[AlertJobMatchResponse] = []
