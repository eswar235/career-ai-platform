"""
Admin Service - User management, auditing, and system monitoring
"""

import logging
import uuid
from typing import List, Tuple, Optional, Dict
from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from app.models.user import User
from app.models.admin import AuditLog, SystemEvent, SystemMetric, UserSuspension
from app.models.application import JobApplication
from app.models.job import Job

logger = logging.getLogger(__name__)


class AuditService:
    """Audit logging service"""

    @staticmethod
    def log_action(
        db: Session,
        action_type: str,
        entity_type: str,
        user_id: Optional[uuid.UUID] = None,
        admin_id: Optional[uuid.UUID] = None,
        entity_id: Optional[uuid.UUID] = None,
        changes: Optional[Dict] = None,
        reason: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuditLog:
        """Log an audit event"""
        try:
            log = AuditLog(
                user_id=user_id,
                admin_id=admin_id,
                action_type=action_type,
                entity_type=entity_type,
                entity_id=entity_id,
                changes=changes,
                reason=reason,
                ip_address=ip_address,
                user_agent=user_agent,
            )
            db.add(log)
            db.commit()
            db.refresh(log)
            logger.info(f"Audit log created: {action_type} on {entity_type}")
            return log

        except Exception as e:
            logger.error(f"Error creating audit log: {str(e)}")
            db.rollback()
            raise

    @staticmethod
    def get_audit_logs(
        db: Session,
        user_id: Optional[uuid.UUID] = None,
        action_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[int, List[AuditLog]]:
        """Get audit logs with filtering"""
        try:
            query = db.query(AuditLog)

            if user_id:
                query = query.filter(AuditLog.user_id == user_id)

            if action_type:
                query = query.filter(AuditLog.action_type == action_type)

            total = query.count()
            logs = query.order_by(desc(AuditLog.created_at)).offset(skip).limit(limit).all()

            return total, logs

        except Exception as e:
            logger.error(f"Error retrieving audit logs: {str(e)}")
            raise


class UserManagementService:
    """User management service"""

    @staticmethod
    def get_all_users(
        db: Session,
        skip: int = 0,
        limit: int = 50,
        is_active: Optional[bool] = None,
    ) -> Tuple[int, List[User]]:
        """Get all users for admin"""
        try:
            query = db.query(User)

            if is_active is not None:
                query = query.filter(User.is_active == is_active)

            total = query.count()
            users = query.order_by(desc(User.created_at)).offset(skip).limit(limit).all()

            return total, users

        except Exception as e:
            logger.error(f"Error retrieving users: {str(e)}")
            raise

    @staticmethod
    def get_user_details(db: Session, user_id: uuid.UUID) -> Optional[User]:
        """Get detailed user information"""
        try:
            return db.query(User).filter(User.id == user_id).first()
        except Exception as e:
            logger.error(f"Error retrieving user details: {str(e)}")
            raise

    @staticmethod
    def update_user(
        db: Session,
        user_id: uuid.UUID,
        is_active: Optional[bool] = None,
        is_admin: Optional[bool] = None,
        is_superuser: Optional[bool] = None,
        admin_id: Optional[uuid.UUID] = None,
    ) -> User:
        """Update user by admin"""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError(f"User not found: {user_id}")

            changes = {}

            if is_active is not None and user.is_active != is_active:
                changes["is_active"] = {"old": user.is_active, "new": is_active}
                user.is_active = is_active

            if is_admin is not None and user.is_admin != is_admin:
                changes["is_admin"] = {"old": user.is_admin, "new": is_admin}
                user.is_admin = is_admin

            if is_superuser is not None and user.is_superuser != is_superuser:
                changes["is_superuser"] = {"old": user.is_superuser, "new": is_superuser}
                user.is_superuser = is_superuser

            db.commit()
            db.refresh(user)

            # Log the action
            if changes and admin_id:
                AuditService.log_action(
                    db=db,
                    action_type="update",
                    entity_type="user",
                    user_id=user_id,
                    admin_id=admin_id,
                    entity_id=user_id,
                    changes=changes,
                )

            logger.info(f"User {user_id} updated by admin {admin_id}")
            return user

        except Exception as e:
            logger.error(f"Error updating user: {str(e)}")
            db.rollback()
            raise

    @staticmethod
    def suspend_user(
        db: Session,
        user_id: uuid.UUID,
        reason: str,
        admin_id: uuid.UUID,
        duration_days: Optional[int] = None,
    ) -> UserSuspension:
        """Suspend a user"""
        try:
            # Create suspension record
            suspension = UserSuspension(
                user_id=user_id,
                reason=reason,
                suspended_by=admin_id,
                is_active=True,
            )
            db.add(suspension)

            # Deactivate user
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user.is_active = False

            db.commit()
            db.refresh(suspension)

            # Log the action
            AuditService.log_action(
                db=db,
                action_type="suspend",
                entity_type="user",
                user_id=user_id,
                admin_id=admin_id,
                entity_id=user_id,
                reason=reason,
            )

            logger.info(f"User {user_id} suspended by admin {admin_id}")
            return suspension

        except Exception as e:
            logger.error(f"Error suspending user: {str(e)}")
            db.rollback()
            raise

    @staticmethod
    def unsuspend_user(
        db: Session,
        user_id: uuid.UUID,
        admin_id: uuid.UUID,
        reason: str,
    ) -> User:
        """Unsuspend a user"""
        try:
            # Update suspension record
            suspension = db.query(UserSuspension).filter(
                and_(
                    UserSuspension.user_id == user_id,
                    UserSuspension.is_active == True,
                )
            ).first()

            if suspension:
                suspension.is_active = False
                suspension.unsuspended_at = datetime.utcnow()

            # Reactivate user
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user.is_active = True

            db.commit()

            if user:
                db.refresh(user)

            # Log the action
            AuditService.log_action(
                db=db,
                action_type="unsuspend",
                entity_type="user",
                user_id=user_id,
                admin_id=admin_id,
                entity_id=user_id,
                reason=reason,
            )

            logger.info(f"User {user_id} unsuspended by admin {admin_id}")
            return user

        except Exception as e:
            logger.error(f"Error unsuspending user: {str(e)}")
            db.rollback()
            raise

    @staticmethod
    def get_suspended_users(db: Session) -> List[UserSuspension]:
        """Get all currently suspended users"""
        try:
            suspensions = db.query(UserSuspension).filter(
                UserSuspension.is_active == True
            ).all()
            return suspensions

        except Exception as e:
            logger.error(f"Error retrieving suspended users: {str(e)}")
            raise


class SystemEventService:
    """System event monitoring service"""

    @staticmethod
    def create_event(
        db: Session,
        event_type: str,
        severity: str,
        title: str,
        description: str,
        related_entity: Optional[str] = None,
        related_id: Optional[uuid.UUID] = None,
        metadata: Optional[Dict] = None,
    ) -> SystemEvent:
        """Create a system event"""
        try:
            event = SystemEvent(
                event_type=event_type,
                severity=severity,
                title=title,
                description=description,
                related_entity=related_entity,
                related_id=related_id,
                metadata=metadata,
                resolved=False,
            )
            db.add(event)
            db.commit()
            db.refresh(event)
            logger.info(f"System event created: {event_type} ({severity})")
            return event

        except Exception as e:
            logger.error(f"Error creating system event: {str(e)}")
            db.rollback()
            raise

    @staticmethod
    def get_events(
        db: Session,
        resolved: Optional[bool] = None,
        severity: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[int, List[SystemEvent]]:
        """Get system events"""
        try:
            query = db.query(SystemEvent)

            if resolved is not None:
                query = query.filter(SystemEvent.resolved == resolved)

            if severity:
                query = query.filter(SystemEvent.severity == severity)

            total = query.count()
            events = query.order_by(desc(SystemEvent.created_at)).offset(skip).limit(limit).all()

            return total, events

        except Exception as e:
            logger.error(f"Error retrieving events: {str(e)}")
            raise

    @staticmethod
    def resolve_event(
        db: Session,
        event_id: uuid.UUID,
        notes: Optional[str] = None,
    ) -> SystemEvent:
        """Resolve a system event"""
        try:
            event = db.query(SystemEvent).filter(SystemEvent.id == event_id).first()
            if not event:
                raise ValueError(f"Event not found: {event_id}")

            event.resolved = True
            event.resolved_at = datetime.utcnow()

            db.commit()
            db.refresh(event)
            logger.info(f"System event resolved: {event_id}")
            return event

        except Exception as e:
            logger.error(f"Error resolving event: {str(e)}")
            db.rollback()
            raise

    @staticmethod
    def get_unresolved_count(db: Session) -> int:
        """Get count of unresolved events"""
        try:
            return db.query(SystemEvent).filter(SystemEvent.resolved == False).count()
        except Exception as e:
            logger.error(f"Error getting unresolved count: {str(e)}")
            raise


class SystemMetricsService:
    """System metrics service"""

    @staticmethod
    def record_metric(
        db: Session,
        metric_type: str,
        value: float,
        unit: Optional[str] = None,
        threshold_warning: Optional[float] = None,
        threshold_critical: Optional[float] = None,
    ) -> SystemMetric:
        """Record a system metric"""
        try:
            # Determine status based on thresholds
            status = "normal"
            if threshold_critical and value >= threshold_critical:
                status = "critical"
            elif threshold_warning and value >= threshold_warning:
                status = "warning"

            metric = SystemMetric(
                metric_type=metric_type,
                value=value,
                unit=unit,
                threshold_warning=threshold_warning,
                threshold_critical=threshold_critical,
                status=status,
            )
            db.add(metric)
            db.commit()
            db.refresh(metric)
            logger.info(f"Metric recorded: {metric_type}={value} ({status})")
            return metric

        except Exception as e:
            logger.error(f"Error recording metric: {str(e)}")
            db.rollback()
            raise

    @staticmethod
    def get_recent_metrics(
        db: Session,
        metric_type: Optional[str] = None,
        hours: int = 24,
    ) -> List[SystemMetric]:
        """Get recent metrics"""
        try:
            query = db.query(SystemMetric)

            if metric_type:
                query = query.filter(SystemMetric.metric_type == metric_type)

            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            query = query.filter(SystemMetric.recorded_at >= cutoff_time)

            metrics = query.order_by(desc(SystemMetric.recorded_at)).all()
            return metrics

        except Exception as e:
            logger.error(f"Error retrieving metrics: {str(e)}")
            raise

    @staticmethod
    def get_health_status(db: Session) -> str:
        """Get overall system health status"""
        try:
            critical_count = db.query(SystemMetric).filter(
                SystemMetric.status == "critical"
            ).count()

            warning_count = db.query(SystemMetric).filter(
                SystemMetric.status == "warning"
            ).count()

            if critical_count > 0:
                return "critical"
            elif warning_count > 0:
                return "warning"
            else:
                return "healthy"

        except Exception as e:
            logger.error(f"Error determining health status: {str(e)}")
            raise


class AdminStatsService:
    """Admin statistics service"""

    @staticmethod
    def get_dashboard_stats(db: Session) -> Dict:
        """Get admin dashboard statistics"""
        try:
            stats = {
                "total_users": db.query(User).count(),
                "active_users": db.query(User).filter(User.is_active == True).count(),
                "suspended_users": db.query(UserSuspension).filter(
                    UserSuspension.is_active == True
                ).count(),
                "admin_users": db.query(User).filter(User.is_admin == True).count(),
                "total_applications": db.query(JobApplication).count(),
                "pending_applications": db.query(JobApplication).filter(
                    JobApplication.status == "applied"
                ).count(),
                "rejected_applications": db.query(JobApplication).filter(
                    JobApplication.status == "rejected"
                ).count(),
                "unresolved_events": db.query(SystemEvent).filter(
                    SystemEvent.resolved == False
                ).count(),
            }
            return stats

        except Exception as e:
            logger.error(f"Error getting dashboard stats: {str(e)}")
            raise
