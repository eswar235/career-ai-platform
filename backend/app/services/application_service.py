"""
Job application service for CRUD operations
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Optional, Tuple

from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from app.models.application import JobApplication, ApplicationActivity
from app.models.job import Job
from app.schemas.application import JobApplicationUpdate

logger = logging.getLogger(__name__)


class ApplicationService:
    """Service for job application management"""

    @staticmethod
    def create_application(
        db: Session,
        user_id: uuid.UUID,
        job_id: uuid.UUID,
        applied_via: Optional[str] = None,
        cover_letter_id: Optional[uuid.UUID] = None,
        resume_id: Optional[uuid.UUID] = None,
        notes: Optional[str] = None,
    ) -> JobApplication:
        """Create a new job application"""
        try:
            # Check if application already exists
            existing = (
                db.query(JobApplication)
                .filter(
                    JobApplication.user_id == user_id,
                    JobApplication.job_id == job_id,
                )
                .first()
            )
            if existing:
                raise ValueError("Application already exists for this job")

            application = JobApplication(
                user_id=user_id,
                job_id=job_id,
                status="applied",
                applied_via=applied_via,
                cover_letter_id=cover_letter_id,
                resume_id=resume_id,
                notes=notes,
            )

            db.add(application)
            db.commit()
            db.refresh(application)

            # Log activity
            ApplicationService._log_activity(
                db, application.id, "application_created", "Application submitted"
            )

            logger.info(f"Created application for user {user_id}, job {job_id}")
            return application
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating application: {str(e)}")
            raise ValueError(f"Failed to create application: {str(e)}")

    @staticmethod
    def get_application(
        db: Session,
        application_id: uuid.UUID,
    ) -> Optional[JobApplication]:
        """Get an application by ID"""
        try:
            return (
                db.query(JobApplication)
                .filter(JobApplication.id == application_id)
                .first()
            )
        except Exception as e:
            logger.error(f"Error retrieving application: {str(e)}")
            raise ValueError(f"Failed to retrieve application: {str(e)}")

    @staticmethod
    def get_user_applications(
        db: Session,
        user_id: uuid.UUID,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> Tuple[int, list[JobApplication]]:
        """Get user's applications"""
        try:
            query = db.query(JobApplication).filter(JobApplication.user_id == user_id)

            if status:
                query = query.filter(JobApplication.status == status)

            total = query.count()

            applications = (
                query.order_by(desc(JobApplication.application_date))
                .offset(skip)
                .limit(limit)
                .all()
            )

            return total, applications
        except Exception as e:
            logger.error(f"Error retrieving user applications: {str(e)}")
            raise ValueError(f"Failed to retrieve applications: {str(e)}")

    @staticmethod
    def update_application(
        db: Session,
        application_id: uuid.UUID,
        update_data: JobApplicationUpdate,
    ) -> JobApplication:
        """Update an application"""
        try:
            application = (
                db.query(JobApplication)
                .filter(JobApplication.id == application_id)
                .first()
            )
            if not application:
                raise ValueError("Application not found")

            old_status = application.status

            if update_data.status:
                application.status = update_data.status
            if update_data.notes is not None:
                application.notes = update_data.notes
            if update_data.cover_letter_id:
                application.cover_letter_id = update_data.cover_letter_id
            if update_data.resume_id:
                application.resume_id = update_data.resume_id

            db.commit()
            db.refresh(application)

            # Log status change
            if update_data.status and old_status != update_data.status:
                ApplicationService._log_activity(
                    db,
                    application_id,
                    "status_changed",
                    f"Status changed from {old_status} to {update_data.status}",
                    old_status,
                    update_data.status,
                )

            logger.info(f"Updated application {application_id}")
            return application
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating application: {str(e)}")
            raise ValueError(f"Failed to update application: {str(e)}")

    @staticmethod
    def update_application_status(
        db: Session,
        application_id: uuid.UUID,
        new_status: str,
        notes: Optional[str] = None,
    ) -> JobApplication:
        """Update only the status of an application"""
        try:
            application = (
                db.query(JobApplication)
                .filter(JobApplication.id == application_id)
                .first()
            )
            if not application:
                raise ValueError("Application not found")

            old_status = application.status
            application.status = new_status

            if notes:
                application.notes = (
                    f"{application.notes}\n[{datetime.utcnow().isoformat()}] {notes}"
                    if application.notes
                    else f"[{datetime.utcnow().isoformat()}] {notes}"
                )

            db.commit()
            db.refresh(application)

            # Log activity
            ApplicationService._log_activity(
                db,
                application_id,
                "status_changed",
                notes or f"Status changed to {new_status}",
                old_status,
                new_status,
            )

            logger.info(f"Updated status for application {application_id} to {new_status}")
            return application
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating status: {str(e)}")
            raise ValueError(f"Failed to update status: {str(e)}")

    @staticmethod
    def bulk_update_status(
        db: Session,
        user_id: uuid.UUID,
        application_ids: list[uuid.UUID],
        new_status: str,
        notes: Optional[str] = None,
    ) -> Tuple[int, int]:
        """Bulk update status for multiple applications"""
        try:
            updated = 0
            failed = 0

            for app_id in application_ids:
                try:
                    ApplicationService.update_application_status(
                        db, app_id, new_status, notes
                    )
                    updated += 1
                except Exception as e:
                    logger.warning(f"Failed to update {app_id}: {str(e)}")
                    failed += 1

            logger.info(f"Bulk updated {updated} applications, {failed} failed")
            return updated, failed
        except Exception as e:
            logger.error(f"Error in bulk update: {str(e)}")
            raise ValueError(f"Failed to bulk update: {str(e)}")

    @staticmethod
    def delete_application(
        db: Session,
        application_id: uuid.UUID,
    ) -> None:
        """Delete an application"""
        try:
            application = (
                db.query(JobApplication)
                .filter(JobApplication.id == application_id)
                .first()
            )
            if not application:
                raise ValueError("Application not found")

            db.delete(application)
            db.commit()

            logger.info(f"Deleted application {application_id}")
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting application: {str(e)}")
            raise ValueError(f"Failed to delete application: {str(e)}")

    @staticmethod
    def get_application_for_job(
        db: Session,
        user_id: uuid.UUID,
        job_id: uuid.UUID,
    ) -> Optional[JobApplication]:
        """Get application for a specific job"""
        try:
            return (
                db.query(JobApplication)
                .filter(
                    JobApplication.user_id == user_id,
                    JobApplication.job_id == job_id,
                )
                .first()
            )
        except Exception as e:
            logger.error(f"Error retrieving application for job: {str(e)}")
            raise ValueError(f"Failed to retrieve application: {str(e)}")

    @staticmethod
    def _log_activity(
        db: Session,
        application_id: uuid.UUID,
        activity_type: str,
        description: Optional[str] = None,
        previous_status: Optional[str] = None,
        new_status: Optional[str] = None,
    ) -> None:
        """Log an activity for an application"""
        try:
            activity = ApplicationActivity(
                application_id=application_id,
                activity_type=activity_type,
                description=description,
                previous_status=previous_status,
                new_status=new_status,
            )
            db.add(activity)
            db.commit()
        except Exception as e:
            logger.warning(f"Failed to log activity: {str(e)}")
