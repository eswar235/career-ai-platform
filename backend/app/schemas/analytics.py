"""
Analytics and dashboard schemas
"""

from datetime import datetime, date
from typing import Optional, List, Dict
from uuid import UUID

from pydantic import BaseModel


# Application Statistics Schemas
class ApplicationStatisticsResponse(BaseModel):
    """Application statistics response"""
    id: UUID
    user_id: UUID
    total_submitted: int
    total_pending: int
    total_rejected: int
    total_interviews: int
    total_offers: int
    response_rate: Optional[float] = None
    average_response_time_days: Optional[float] = None
    success_rate: Optional[float] = None
    last_updated: datetime

    class Config:
        from_attributes = True


# Trends Schemas
class ApplicationTrendResponse(BaseModel):
    """Single day trend response"""
    id: UUID
    user_id: UUID
    date: date
    applications_submitted: int
    applications_reviewed: int
    interviews_scheduled: int
    rejections_received: int
    offers_received: int

    class Config:
        from_attributes = True


class TrendsResponse(BaseModel):
    """Trends over time period"""
    period: str  # "30days", "90days", "all_time"
    trends: List[ApplicationTrendResponse]
    total_applications: int
    average_per_day: float
    peak_day: Optional[date] = None


# Role Analytics Schemas
class RoleAnalyticsResponse(BaseModel):
    """Role analytics response"""
    id: UUID
    job_title: str
    application_count: int
    interview_count: int
    offer_count: int
    rejection_count: int
    last_applied: Optional[date] = None
    success_rate: Optional[float] = None

    class Config:
        from_attributes = True


# Company Analytics Schemas
class CompanyAnalyticsResponse(BaseModel):
    """Company analytics response"""
    id: UUID
    company_name: str
    application_count: int
    interview_count: int
    offer_count: int
    rejection_count: int
    last_applied: Optional[date] = None
    success_rate: Optional[float] = None

    class Config:
        from_attributes = True


# Source Analytics Schemas
class SourceAnalyticsResponse(BaseModel):
    """Source analytics response"""
    id: UUID
    source_name: str
    application_count: int
    interview_count: int
    offer_count: int
    rejection_count: int
    success_rate: Optional[float] = None

    class Config:
        from_attributes = True


# Dashboard Response Schemas
class DashboardMetrics(BaseModel):
    """Key metrics for dashboard"""
    total_applications: int
    pending_applications: int
    rejected_applications: int
    interview_scheduled: int
    offers_received: int
    response_rate: Optional[float] = None
    success_rate: Optional[float] = None
    average_response_time: Optional[float] = None


class TopRolesResponse(BaseModel):
    """Top applied-to roles"""
    top_roles: List[RoleAnalyticsResponse]
    total_unique_roles: int


class TopCompaniesResponse(BaseModel):
    """Top companies applied to"""
    top_companies: List[CompanyAnalyticsResponse]
    total_unique_companies: int


class SourceBreakdownResponse(BaseModel):
    """Application breakdown by source"""
    sources: List[SourceAnalyticsResponse]
    total_sources: int


class DashboardResponse(BaseModel):
    """Complete dashboard data"""
    metrics: DashboardMetrics
    top_roles: List[RoleAnalyticsResponse]
    top_companies: List[CompanyAnalyticsResponse]
    sources: List[SourceAnalyticsResponse]
    recent_trends: Optional[List[ApplicationTrendResponse]] = None
    last_updated: datetime


# Export Schemas
class ApplicationExportRecord(BaseModel):
    """Record for CSV export"""
    job_title: str
    company_name: str
    job_source: Optional[str] = None
    submission_date: date
    current_status: str
    resume_version: Optional[str] = None
    cover_letter_version: Optional[str] = None


class ExportResponse(BaseModel):
    """Export response"""
    total_records: int
    records: List[ApplicationExportRecord]
    exported_at: datetime


# Period Request Schema
class AnalyticsPeriodRequest(BaseModel):
    """Request for analytics with time period"""
    period: str = "30days"  # 30days, 90days, all_time


# Status Breakdown Schemas
class StatusBreakdownResponse(BaseModel):
    """Application breakdown by status"""
    status: str
    count: int
    percentage: float


class DetailedBreakdownResponse(BaseModel):
    """Detailed breakdown by status"""
    by_status: List[StatusBreakdownResponse]
    by_title: Dict[str, int]
    by_company: Dict[str, int]
    by_source: Dict[str, int]
    by_experience_level: Dict[str, int]


# Insights Schemas
class ApplicationInsight(BaseModel):
    """Application insight"""
    insight_type: str  # "strength", "opportunity", "warning"
    title: str
    description: str
    metric: Optional[float] = None


class InsightsResponse(BaseModel):
    """Application insights"""
    insights: List[ApplicationInsight]
    generated_at: datetime
