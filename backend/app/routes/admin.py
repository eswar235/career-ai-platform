"""
Admin panel API routes
"""

import logging
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query

from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.admin import (
    UserManagementResponse,
    UserListResponse,
    UserUpdateRequest,
    UserSuspendRequest,
    UserUnsuspendRequest,
    AuditLogResponse,
    AuditLogListResponse,
    SystemEventResponse,
    SystemEventListResponse,
    ResolveEventRequest,
    SystemMetricResponse,
    MetricsOverviewResponse,
    UserSuspensionResponse,
    AdminDashboardResponse,
    AdminDashboardStats,
)
from app.services.admin_service import (
    AuditService,
    UserManagementService,
    SystemEventService,
    SystemMetricsService,
    AdminStatsService,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin", tags=["admin"])


def verify_admin(current_user: User = Depends(get_current_user)):
    """Verify user is admin"""
    if not current_user.is_admin and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


# User Management Endpoints
@router.get("/users", response_model=UserListResponse)
def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    is_active: bool = Query(None),
    admin_user: User = Depends(verify_admin),
    db: Session = Depends(get_db),
):
    """List all users"""
    try:
        total, users = UserManagementService.get_all_users(db, skip, limit, is_active)
        return UserListResponse(
            total=total,
            users=[UserManagementResponse.from_orm(u) for u in users],
            page=skip // limit + 1,
            limit=limit,
        )
    except Exception as e:
        logger.error(f"Error listing users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list users",
        )


@router.get("/users/{user_id}", response_model=UserManagementResponse)
def get_user(
    user_id: uuid.UUID,
    admin_user: User = Depends(verify_admin),
    db: Session = Depends(get_db),
):
    """Get user details"""
    try:
        user = UserManagementService.get_user_details(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        return UserManagementResponse.from_orm(user)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user",
        )


@router.put("/users/{user_id}", response_model=UserManagementResponse)
def update_user(
    user_id: uuid.UUID,
    request: UserUpdateRequest,
    admin_user: User = Depends(verify_admin),
    db: Session = Depends(get_db),
):
    """Update user by admin"""
    try:
        user = UserManagementService.update_user(
            db,
            user_id,
            is_active=request.is_active,
            is_admin=request.is_admin,
            is_superuser=request.is_superuser,
            admin_id=admin_user.id,
        )
        return UserManagementResponse.from_orm(user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user",
        )


@router.post("/users/{user_id}/suspend", response_model=UserSuspensionResponse)
def suspend_user(
    user_id: uuid.UUID,
    request: UserSuspendRequest,
    admin_user: User = Depends(verify_admin),
    db: Session = Depends(get_db),
):
    """Suspend a user"""
    try:
        suspension = UserManagementService.suspend_user(
            db,
            user_id,
            request.reason,
            admin_user.id,
            request.duration_days,
        )
        return UserSuspensionResponse.from_orm(suspension)
    except Exception as e:
        logger.error(f"Error suspending user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to suspend user",
        )


@router.post("/users/{user_id}/unsuspend", response_model=UserManagementResponse)
def unsuspend_user(
    user_id: uuid.UUID,
    request: UserUnsuspendRequest,
    admin_user: User = Depends(verify_admin),
    db: Session = Depends(get_db),
):
    """Unsuspend a user"""
    try:
        user = UserManagementService.unsuspend_user(
            db,
            user_id,
            admin_user.id,
            request.reason,
        )
        return UserManagementResponse.from_orm(user)
    except Exception as e:
        logger.error(f"Error unsuspending user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to unsuspend user",
        )


# Audit Log Endpoints
@router.get("/audit-logs", response_model=AuditLogListResponse)
def get_audit_logs(
    user_id: uuid.UUID = Query(None),
    action_type: str = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    admin_user: User = Depends(verify_admin),
    db: Session = Depends(get_db),
):
    """Get audit logs"""
    try:
        total, logs = AuditService.get_audit_logs(
            db, user_id, action_type, skip, limit
        )
        return AuditLogListResponse(
            total=total,
            logs=[AuditLogResponse.from_orm(l) for l in logs],
            page=skip // limit + 1,
            limit=limit,
        )
    except Exception as e:
        logger.error(f"Error retrieving audit logs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve audit logs",
        )


# System Event Endpoints
@router.get("/events", response_model=SystemEventListResponse)
def get_system_events(
    resolved: bool = Query(None),
    severity: str = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    admin_user: User = Depends(verify_admin),
    db: Session = Depends(get_db),
):
    """Get system events"""
    try:
        total, events = SystemEventService.get_events(
            db, resolved, severity, skip, limit
        )
        unresolved = SystemEventService.get_unresolved_count(db)
        critical = sum(1 for e in events if e.severity == "critical" and not e.resolved)

        return SystemEventListResponse(
            total=total,
            events=[SystemEventResponse.from_orm(e) for e in events],
            unresolved_count=unresolved,
            critical_count=critical,
            page=skip // limit + 1,
            limit=limit,
        )
    except Exception as e:
        logger.error(f"Error retrieving events: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve events",
        )


@router.put("/events/{event_id}/resolve", response_model=SystemEventResponse)
def resolve_event(
    event_id: uuid.UUID,
    request: ResolveEventRequest,
    admin_user: User = Depends(verify_admin),
    db: Session = Depends(get_db),
):
    """Resolve a system event"""
    try:
        event = SystemEventService.resolve_event(db, event_id, request.notes)
        return SystemEventResponse.from_orm(event)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error resolving event: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to resolve event",
        )


# System Metrics Endpoints
@router.get("/metrics", response_model=MetricsOverviewResponse)
def get_system_metrics(
    metric_type: str = Query(None),
    hours: int = Query(24, ge=1, le=720),
    admin_user: User = Depends(verify_admin),
    db: Session = Depends(get_db),
):
    """Get system metrics"""
    try:
        metrics = SystemMetricsService.get_recent_metrics(db, metric_type, hours)
        health_status = SystemMetricsService.get_health_status(db)
        critical_issues = [m.title for m in metrics if m.status == "critical"]

        return MetricsOverviewResponse(
            timestamp=datetime.utcnow(),
            metrics=[SystemMetricResponse.from_orm(m) for m in metrics],
            health_status=health_status,
            critical_issues=critical_issues,
        )
    except Exception as e:
        logger.error(f"Error retrieving metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve metrics",
        )


# Dashboard Endpoint
@router.get("/dashboard", response_model=AdminDashboardResponse)
def get_admin_dashboard(
    admin_user: User = Depends(verify_admin),
    db: Session = Depends(get_db),
):
    """Get admin dashboard"""
    try:
        stats = AdminStatsService.get_dashboard_stats(db)
        recent_logs = AuditService.get_audit_logs(db, skip=0, limit=10)[1]
        system_events = SystemEventService.get_events(db, resolved=False, skip=0, limit=10)[1]
        metrics = SystemMetricsService.get_recent_metrics(db, hours=24)
        health_status = SystemMetricsService.get_health_status(db)

        return AdminDashboardResponse(
            stats=AdminDashboardStats(**stats),
            recent_audit_logs=[AuditLogResponse.from_orm(l) for l in recent_logs],
            system_events=[SystemEventResponse.from_orm(e) for e in system_events],
            recent_suspensions=[],  # Placeholder
            metrics=MetricsOverviewResponse(
                timestamp=datetime.utcnow(),
                metrics=[SystemMetricResponse.from_orm(m) for m in metrics],
                health_status=health_status,
            ),
            last_updated=datetime.utcnow(),
        )
    except Exception as e:
        logger.error(f"Error getting dashboard: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get dashboard",
        )


# Removed duplicate import
