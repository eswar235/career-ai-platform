"""
Notification Service - Manage in-app and email notifications
"""

import logging
import uuid
from typing import List, Tuple, Optional
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.notification import (
    Notification,
    EmailNotification,
    NotificationPreferences,
)
from app.models.user import User

logger = logging.getLogger(__name__)


class NotificationService:
    """In-app notification service"""

    @staticmethod
    def create_notification(
        db: Session,
        user_id: uuid.UUID,
        notification_type: str,
        title: str,
        message: str,
        related_entity_type: Optional[str] = None,
        related_entity_id: Optional[uuid.UUID] = None,
    ) -> Notification:
        """Create in-app notification"""
        try:
            notification = Notification(
                user_id=user_id,
                notification_type=notification_type,
                title=title,
                message=message,
                related_entity_type=related_entity_type,
                related_entity_id=related_entity_id,
                is_read=False,
            )
            db.add(notification)
            db.commit()
            db.refresh(notification)
            logger.info(f"Notification created for user {user_id}: {notification_type}")
            return notification

        except Exception as e:
            logger.error(f"Error creating notification: {str(e)}")
            db.rollback()
            raise

    @staticmethod
    def get_notification(db: Session, notification_id: uuid.UUID) -> Optional[Notification]:
        """Get single notification"""
        try:
            return db.query(Notification).filter(Notification.id == notification_id).first()
        except Exception as e:
            logger.error(f"Error retrieving notification: {str(e)}")
            raise

    @staticmethod
    def get_user_notifications(
        db: Session,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 20,
        unread_only: bool = False,
    ) -> Tuple[int, List[Notification]]:
        """Get user's notifications"""
        try:
            query = db.query(Notification).filter(Notification.user_id == user_id)

            if unread_only:
                query = query.filter(Notification.is_read == False)

            total = query.count()
            notifications = query.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()
            logger.info(f"Retrieved {len(notifications)} notifications for user {user_id}")
            return total, notifications

        except Exception as e:
            logger.error(f"Error retrieving user notifications: {str(e)}")
            raise

    @staticmethod
    def mark_as_read(db: Session, notification_id: uuid.UUID) -> Notification:
        """Mark notification as read"""
        try:
            notification = db.query(Notification).filter(Notification.id == notification_id).first()
            if not notification:
                raise ValueError(f"Notification not found: {notification_id}")

            notification.is_read = True
            notification.read_at = datetime.utcnow()
            db.commit()
            db.refresh(notification)
            logger.info(f"Notification marked as read: {notification_id}")
            return notification

        except Exception as e:
            logger.error(f"Error marking notification as read: {str(e)}")
            db.rollback()
            raise

    @staticmethod
    def mark_all_as_read(db: Session, user_id: uuid.UUID) -> int:
        """Mark all user notifications as read"""
        try:
            notifications = db.query(Notification).filter(
                and_(
                    Notification.user_id == user_id,
                    Notification.is_read == False,
                )
            ).all()

            for notification in notifications:
                notification.is_read = True
                notification.read_at = datetime.utcnow()

            db.commit()
            logger.info(f"Marked {len(notifications)} notifications as read for user {user_id}")
            return len(notifications)

        except Exception as e:
            logger.error(f"Error marking all notifications as read: {str(e)}")
            db.rollback()
            raise

    @staticmethod
    def delete_notification(db: Session, notification_id: uuid.UUID) -> None:
        """Delete notification"""
        try:
            notification = db.query(Notification).filter(Notification.id == notification_id).first()
            if not notification:
                raise ValueError(f"Notification not found: {notification_id}")

            db.delete(notification)
            db.commit()
            logger.info(f"Notification deleted: {notification_id}")

        except Exception as e:
            logger.error(f"Error deleting notification: {str(e)}")
            db.rollback()
            raise

    @staticmethod
    def get_unread_count(db: Session, user_id: uuid.UUID) -> int:
        """Get unread notification count"""
        try:
            count = db.query(Notification).filter(
                and_(
                    Notification.user_id == user_id,
                    Notification.is_read == False,
                )
            ).count()
            return count

        except Exception as e:
            logger.error(f"Error getting unread count: {str(e)}")
            raise


class EmailNotificationService:
    """Email notification service"""

    @staticmethod
    def create_email_notification(
        db: Session,
        user_id: uuid.UUID,
        email_address: str,
        notification_type: str,
        subject: str,
        body: str,
    ) -> EmailNotification:
        """Create email notification record"""
        try:
            email_notif = EmailNotification(
                user_id=user_id,
                email_address=email_address,
                notification_type=notification_type,
                subject=subject,
                body=body,
                status="pending",
            )
            db.add(email_notif)
            db.commit()
            db.refresh(email_notif)
            logger.info(f"Email notification created for user {user_id}: {notification_type}")
            return email_notif

        except Exception as e:
            logger.error(f"Error creating email notification: {str(e)}")
            db.rollback()
            raise

    @staticmethod
    def mark_sent(
        db: Session,
        email_notif_id: uuid.UUID,
        sent_at: Optional[datetime] = None,
    ) -> EmailNotification:
        """Mark email as sent"""
        try:
            email_notif = db.query(EmailNotification).filter(
                EmailNotification.id == email_notif_id
            ).first()
            if not email_notif:
                raise ValueError(f"Email notification not found: {email_notif_id}")

            email_notif.status = "sent"
            email_notif.sent_at = sent_at or datetime.utcnow()
            db.commit()
            db.refresh(email_notif)
            logger.info(f"Email notification marked as sent: {email_notif_id}")
            return email_notif

        except Exception as e:
            logger.error(f"Error marking email as sent: {str(e)}")
            db.rollback()
            raise

    @staticmethod
    def mark_failed(
        db: Session,
        email_notif_id: uuid.UUID,
        error: str,
    ) -> EmailNotification:
        """Mark email as failed"""
        try:
            email_notif = db.query(EmailNotification).filter(
                EmailNotification.id == email_notif_id
            ).first()
            if not email_notif:
                raise ValueError(f"Email notification not found: {email_notif_id}")

            email_notif.status = "failed"
            email_notif.delivery_error = error
            db.commit()
            db.refresh(email_notif)
            logger.info(f"Email notification marked as failed: {email_notif_id}")
            return email_notif

        except Exception as e:
            logger.error(f"Error marking email as failed: {str(e)}")
            db.rollback()
            raise

    @staticmethod
    def get_pending_emails(db: Session, limit: int = 100) -> List[EmailNotification]:
        """Get pending email notifications"""
        try:
            emails = db.query(EmailNotification).filter(
                EmailNotification.status == "pending"
            ).limit(limit).all()
            logger.info(f"Retrieved {len(emails)} pending emails")
            return emails

        except Exception as e:
            logger.error(f"Error retrieving pending emails: {str(e)}")
            raise


class NotificationPreferencesService:
    """Notification preferences service"""

    @staticmethod
    def get_or_create_preferences(
        db: Session,
        user_id: uuid.UUID,
    ) -> NotificationPreferences:
        """Get or create notification preferences"""
        try:
            prefs = db.query(NotificationPreferences).filter(
                NotificationPreferences.user_id == user_id
            ).first()

            if not prefs:
                prefs = NotificationPreferences(
                    user_id=user_id,
                    job_alerts_enabled=True,
                    application_updates_enabled=True,
                    interview_reminders_enabled=True,
                    daily_digest_enabled=False,
                    email_notifications_enabled=True,
                    in_app_notifications_enabled=True,
                )
                db.add(prefs)
                db.commit()
                db.refresh(prefs)
                logger.info(f"Notification preferences created for user {user_id}")

            return prefs

        except Exception as e:
            logger.error(f"Error getting/creating preferences: {str(e)}")
            db.rollback()
            raise

    @staticmethod
    def get_preferences(db: Session, user_id: uuid.UUID) -> Optional[NotificationPreferences]:
        """Get notification preferences"""
        try:
            return db.query(NotificationPreferences).filter(
                NotificationPreferences.user_id == user_id
            ).first()
        except Exception as e:
            logger.error(f"Error retrieving preferences: {str(e)}")
            raise

    @staticmethod
    def update_preferences(
        db: Session,
        user_id: uuid.UUID,
        **kwargs,
    ) -> NotificationPreferences:
        """Update notification preferences"""
        try:
            prefs = NotificationPreferencesService.get_or_create_preferences(db, user_id)

            for key, value in kwargs.items():
                if hasattr(prefs, key) and value is not None:
                    setattr(prefs, key, value)

            prefs.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(prefs)
            logger.info(f"Notification preferences updated for user {user_id}")
            return prefs

        except Exception as e:
            logger.error(f"Error updating preferences: {str(e)}")
            db.rollback()
            raise
