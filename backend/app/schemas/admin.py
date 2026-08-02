"""
Admin panel schemas
"""

from datetime import datetime
from typing import Optional, List, Dict
from uuid import UUID

from pydantic import BaseModel, Field


# User Management Schemas
class UserManagementResponse(BaseModel):
    """User for admin management"""
    id: UUID
    email: str
    full_name: Optional[str] = None
    is_active: bool
    is_admin: bool
    is_superuser: bool
    email_verified: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """Paginated user list"""
    total: int
    users: List[UserManagementResponse]
    page: int
    limit: int


class UserUpdateRequest(BaseModel):
    """Update user request"""
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None
    is_superuser: Optional[bool] = None
    permissions: Optional[Dict] = None


class UserSuspendRequest(BaseModel):
    """Suspend user request"""
    reason: str = Field(..., min_length=10, max_length=1000)
    duration_days: Optional[int] = None  # None = indefinite


class UserUnsuspendRequest(BaseModel):
    """Unsuspend user request"""
    reason: str = Field(..., min_length=10, max_length=500)


# Audit Log Schemas
class AuditLogResponse(BaseModel):
    """Audit log response"""
    id: UUID
    user_id: Optional[UUID] = None
    admin_id: Optional[UUID] = None
    action_type: str
    entity_type: str
    entity_id: Optional[UUID] = None
    changes: Optional[Dict] = None
    reason: Optional[str] = None
    ip_address: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AuditLogListResponse(BaseModel):
    """Paginated audit log list"""
    total: int
    logs: List[AuditLogResponse]
    page: int
    limit: int


# System Event Schemas
class SystemEventResponse(BaseModel):
    """System event response"""
    id: UUID
    event_type: str
    severity: str
    title: str
    description: str
    related_entity: Optional[str] = None
    related_id: Optional[UUID] = None
    resolved: bool
    resolved_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class SystemEventListResponse(BaseModel):
    """Paginated system event list"""
    total: int
    events: List[SystemEventResponse]
    unresolved_count: int
    critical_count: int
    page: int
    limit: int


class ResolveEventRequest(BaseModel):
    """Resolve system event request"""
    resolved: bool = True
    notes: Optional[str] = None


# System Metrics Schemas
class SystemMetricResponse(BaseModel):
    """System metric response"""
    id: UUID
    metric_type: str
    value: float
    unit: Optional[str] = None
    status: str
    recorded_at: datetime

    class Config:
        from_attributes = True


class MetricsOverviewResponse(BaseModel):
    """System metrics overview"""
    timestamp: datetime
    metrics: List[SystemMetricResponse]
    health_status: str  # healthy, warning, critical
    critical_issues: List[str] = []


# User Suspension Schemas
class UserSuspensionResponse(BaseModel):
    """User suspension response"""
    id: UUID
    user_id: UUID
    reason: str
    suspended_by: UUID
    suspended_at: datetime
    unsuspended_at: Optional[datetime] = None
    is_active: bool

    class Config:
        from_attributes = True


# Dashboard Schemas
class AdminDashboardStats(BaseModel):
    """Admin dashboard statistics"""
    total_users: int
    active_users: int
    suspended_users: int
    admin_users: int
    total_applications: int
    pending_applications: int
    rejected_applications: int
    system_health: str
    unresolved_events: int


class AdminDashboardResponse(BaseModel):
    """Complete admin dashboard"""
    stats: AdminDashboardStats
    recent_audit_logs: List[AuditLogResponse]
    system_events: List[SystemEventResponse]
    recent_suspensions: List[UserSuspensionResponse]
    metrics: MetricsOverviewResponse
    last_updated: datetime


# User Deletion Request Schemas
class UserDataExportRequest(BaseModel):
    """Request user data export"""
    format: str = Field(default="json", regex="^(json|csv)$")


class UserDeleteRequest(BaseModel):
    """Request user deletion"""
    reason: str = Field(..., min_length=10, max_length=1000)
    notify_user: bool = Field(default=True)


# Job Management Schemas
class JobManagementResponse(BaseModel):
    """Job for admin management"""
    id: UUID
    title: str
    company_name: str
    source: Optional[str] = None
    is_active: bool
    created_at: datetime
    applications_count: Optional[int] = None

    class Config:
        from_attributes = True


class JobListResponse(BaseModel):
    """Paginated job list"""
    total: int
    jobs: List[JobManagementResponse]
    page: int
    limit: int


class JobDeactivateRequest(BaseModel):
    """Deactivate job request"""
    reason: str = Field(..., min_length=10, max_length=500)


# System Configuration Schemas
class SystemConfigResponse(BaseModel):
    """System configuration"""
    maintenance_mode: bool
    rate_limit_enabled: bool
    max_requests_per_minute: int
    email_notifications_enabled: bool
    job_alert_enabled: bool
    feature_flags: Dict[str, bool]
    last_updated: datetime


class SystemConfigUpdateRequest(BaseModel):
    """Update system configuration"""
    maintenance_mode: Optional[bool] = None
    rate_limit_enabled: Optional[bool] = None
    max_requests_per_minute: Optional[int] = None
    email_notifications_enabled: Optional[bool] = None
    job_alert_enabled: Optional[bool] = None
    feature_flags: Optional[Dict[str, bool]] = None
