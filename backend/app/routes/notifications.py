"""
Notification API routes
"""

import logging
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Query

from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.notification import (
    JobAlertCreate,
    JobAlertUpdate,
    JobAlertResponse,
    NotificationResponse,
    NotificationMarkReadRequest,
    EmailNotificationResponse,
    AlertJobMatchResponse,
    NotificationPreferencesUpdate,
    NotificationPreferencesResponse,
    NotificationsSummaryResponse,
    AlertMatchesResponse,
)
from app.services.job_alert_service import JobAlertService
from app.services.notification_service import (
    NotificationService,
    EmailNotificationService,
    NotificationPreferencesService,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


# Job Alert Endpoints
@router.post("/alerts", response_model=JobAlertResponse)
def create_or_update_alert(
    request: JobAlertCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create or update job alert"""
    try:
        alert = JobAlertService.create_or_get_alert(
            db=db,
            user_id=current_user.id,
            keywords=request.keywords,
            locations=request.locations,
            job_titles=request.job_titles,
            experience_levels=request.experience_levels,
            salary_min=request.salary_min,
            salary_max=request.salary_max,
            min_match_score=request.min_match_score,
            notification_frequency=request.notification_frequency,
            preferred_time=request.preferred_time,
        )
        return alert
    except Exception as e:
        logger.error(f"Error creating alert: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                          detail="Failed to create alert")


@router.get("/alerts", response_model=JobAlertResponse)
def get_alert(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get user's job alert"""
    try:
        alert = JobAlertService.get_alert(db, current_user.id)
        if not alert:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                              detail="Alert not found")
        return alert
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving alert: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                          detail="Failed to retrieve alert")


@router.put("/alerts", response_model=JobAlertResponse)
def update_alert(
    request: JobAlertUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update job alert"""
    try:
        update_data = request.dict(exclude_unset=True)
        alert = JobAlertService.update_alert(db, current_user.id, **update_data)
        return alert
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating alert: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                          detail="Failed to update alert")


@router.post("/alerts/toggle", response_model=JobAlertResponse)
def toggle_alert(
    is_active: bool = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Toggle job alert on/off"""
    try:
        alert = JobAlertService.toggle_alert(db, current_user.id, is_active)
        return alert
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error toggling alert: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                          detail="Failed to toggle alert")


# Alert Matches Endpoints
@router.get("/alert-matches", response_model=AlertMatchesResponse)
def get_alert_matches(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get user's alert matches"""
    try:
        total, matches = JobAlertService.get_user_matches(db, current_user.id, skip, limit)
        return {
            "total_matches": total,
            "new_matches": sum(1 for m in matches if not m.notification_sent),
            "matches": matches,
        }
    except Exception as e:
        logger.error(f"Error retrieving alert matches: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                          detail="Failed to retrieve alert matches")


@router.post("/alert-matches/{match_id}/dismiss", response_model=AlertJobMatchResponse)
def dismiss_match(
    match_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Dismiss alert match"""
    try:
        match = JobAlertService.dismiss_match(db, match_id)
        return match
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error dismissing match: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                          detail="Failed to dismiss match")


# Notification Endpoints
@router.get("", response_model=NotificationsSummaryResponse)
def get_notifications(
    unread_only: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get user notifications"""
    try:
        total, notifications = NotificationService.get_user_notifications(
            db, current_user.id, skip, limit, unread_only
        )
        unread_count = NotificationService.get_unread_count(db, current_user.id)

        return {
            "total_unread": unread_count,
            "total_notifications": total,
            "job_alerts_count": sum(1 for n in notifications if n.notification_type == "job_alert"),
            "application_updates_count": sum(1 for n in notifications if n.notification_type == "application_update"),
            "interview_reminders_count": sum(1 for n in notifications if n.notification_type == "interview_reminder"),
            "notifications": notifications,
        }
    except Exception as e:
        logger.error(f"Error retrieving notifications: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                          detail="Failed to retrieve notifications")


@router.get("/{notification_id}", response_model=NotificationResponse)
def get_notification(
    notification_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get single notification"""
    try:
        notification = NotificationService.get_notification(db, notification_id)
        if not notification or notification.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                              detail="Notification not found")
        return notification
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving notification: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                          detail="Failed to retrieve notification")


@router.put("/{notification_id}/read", response_model=NotificationResponse)
def mark_notification_read(
    notification_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Mark notification as read"""
    try:
        notification = NotificationService.get_notification(db, notification_id)
        if not notification or notification.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                              detail="Notification not found")

        notification = NotificationService.mark_as_read(db, notification_id)
        return notification
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking notification as read: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                          detail="Failed to mark notification as read")


@router.post("/read-all", response_model=dict)
def mark_all_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Mark all notifications as read"""
    try:
        count = NotificationService.mark_all_as_read(db, current_user.id)
        return {"marked_as_read": count}
    except Exception as e:
        logger.error(f"Error marking all as read: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                          detail="Failed to mark all as read")


@router.delete("/{notification_id}")
def delete_notification(
    notification_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete notification"""
    try:
        notification = NotificationService.get_notification(db, notification_id)
        if not notification or notification.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                              detail="Notification not found")

        NotificationService.delete_notification(db, notification_id)
        return {"deleted": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting notification: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                          detail="Failed to delete notification")


# Notification Preferences Endpoints
@router.get("/preferences", response_model=NotificationPreferencesResponse)
def get_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get notification preferences"""
    try:
        prefs = NotificationPreferencesService.get_or_create_preferences(db, current_user.id)
        return prefs
    except Exception as e:
        logger.error(f"Error retrieving preferences: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                          detail="Failed to retrieve preferences")


@router.put("/preferences", response_model=NotificationPreferencesResponse)
def update_preferences(
    request: NotificationPreferencesUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update notification preferences"""
    try:
        update_data = request.dict(exclude_unset=True)
        prefs = NotificationPreferencesService.update_preferences(db, current_user.id, **update_data)
        return prefs
    except Exception as e:
        logger.error(f"Error updating preferences: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                          detail="Failed to update preferences")
