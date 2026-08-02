"""
Automation job service for managing automation tasks
"""

import logging
import uuid
from datetime import datetime
from typing import Optional, Tuple

from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.automation import AutomationJob, AutomationStep, AutomationLog
from app.schemas.automation import AutomationJobUpdate

logger = logging.getLogger(__name__)


class AutomationService:
    """Service for automation job management"""

    @staticmethod
    def create_automation_job(
        db: Session,
        user_id: uuid.UUID,
        job_id: uuid.UUID,
        job_url: str,
        automation_type: Optional[str] = None,
        browser_type: str = "chrome",
        headless: bool = True,
        max_retries: int = 3,
    ) -> AutomationJob:
        """Create a new automation job"""
        try:
            job = AutomationJob(
                user_id=user_id,
                job_id=job_id,
                job_url=job_url,
                automation_type=automation_type,
                browser_type=browser_type,
                headless=headless,
                max_retries=max_retries,
                status="pending",
            )

            db.add(job)
            db.commit()
            db.refresh(job)

            logger.info(f"Created automation job for user {user_id}, job {job_id}")
            return job
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating automation job: {str(e)}")
            raise ValueError(f"Failed to create automation job: {str(e)}")

    @staticmethod
    def get_automation_job(
        db: Session,
        automation_id: uuid.UUID,
    ) -> Optional[AutomationJob]:
        """Get automation job by ID"""
        try:
            return (
                db.query(AutomationJob)
                .filter(AutomationJob.id == automation_id)
                .first()
            )
        except Exception as e:
            logger.error(f"Error retrieving automation job: {str(e)}")
            raise ValueError(f"Failed to retrieve automation job: {str(e)}")

    @staticmethod
    def get_user_automation_jobs(
        db: Session,
        user_id: uuid.UUID,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> Tuple[int, list[AutomationJob]]:
        """Get user's automation jobs"""
        try:
            query = db.query(AutomationJob).filter(AutomationJob.user_id == user_id)

            if status:
                query = query.filter(AutomationJob.status == status)

            total = query.count()

            jobs = (
                query.order_by(desc(AutomationJob.created_at))
                .offset(skip)
                .limit(limit)
                .all()
            )

            return total, jobs
        except Exception as e:
            logger.error(f"Error retrieving automation jobs: {str(e)}")
            raise ValueError(f"Failed to retrieve automation jobs: {str(e)}")

    @staticmethod
    def update_automation_job_status(
        db: Session,
        automation_id: uuid.UUID,
        status: str,
        error_message: Optional[str] = None,
        result: Optional[str] = None,
    ) -> AutomationJob:
        """Update automation job status"""
        try:
            job = (
                db.query(AutomationJob)
                .filter(AutomationJob.id == automation_id)
                .first()
            )
            if not job:
                raise ValueError("Automation job not found")

            job.status = status
            if error_message:
                job.error_message = error_message
            if result:
                job.result = result

            # Set timestamps
            if status == "in_progress" and not job.started_at:
                job.started_at = datetime.utcnow()
            if status in ["completed", "failed"] and not job.completed_at:
                job.completed_at = datetime.utcnow()

            db.commit()
            db.refresh(job)

            logger.info(f"Updated automation job {automation_id} status to {status}")
            return job
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating automation job: {str(e)}")
            raise ValueError(f"Failed to update automation job: {str(e)}")

    @staticmethod
    def increment_retry(db: Session, automation_id: uuid.UUID) -> AutomationJob:
        """Increment retry count"""
        try:
            job = (
                db.query(AutomationJob)
                .filter(AutomationJob.id == automation_id)
                .first()
            )
            if not job:
                raise ValueError("Automation job not found")

            job.current_retry += 1
            db.commit()
            db.refresh(job)

            logger.info(f"Incremented retry count for job {automation_id}")
            return job
        except Exception as e:
            db.rollback()
            logger.error(f"Error incrementing retry: {str(e)}")
            raise ValueError(f"Failed to increment retry: {str(e)}")

    @staticmethod
    def delete_automation_job(
        db: Session,
        automation_id: uuid.UUID,
    ) -> None:
        """Delete automation job"""
        try:
            job = (
                db.query(AutomationJob)
                .filter(AutomationJob.id == automation_id)
                .first()
            )
            if not job:
                raise ValueError("Automation job not found")

            db.delete(job)
            db.commit()

            logger.info(f"Deleted automation job {automation_id}")
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting automation job: {str(e)}")
            raise ValueError(f"Failed to delete automation job: {str(e)}")

    @staticmethod
    def add_automation_step(
        db: Session,
        automation_id: uuid.UUID,
        step_order: int,
        action_type: str,
        step_name: Optional[str] = None,
        selector: Optional[str] = None,
        value: Optional[str] = None,
        wait_time_ms: Optional[int] = None,
        retry_on_fail: bool = False,
    ) -> AutomationStep:
        """Add a step to automation job"""
        try:
            step = AutomationStep(
                automation_job_id=automation_id,
                step_order=step_order,
                action_type=action_type,
                step_name=step_name,
                selector=selector,
                value=value,
                wait_time_ms=wait_time_ms,
                retry_on_fail=retry_on_fail,
            )

            db.add(step)
            db.commit()
            db.refresh(step)

            logger.info(f"Added step to automation job {automation_id}")
            return step
        except Exception as e:
            db.rollback()
            logger.error(f"Error adding automation step: {str(e)}")
            raise ValueError(f"Failed to add automation step: {str(e)}")

    @staticmethod
    def update_step_result(
        db: Session,
        step_id: uuid.UUID,
        success: bool,
        error_message: Optional[str] = None,
    ) -> AutomationStep:
        """Update step execution result"""
        try:
            step = (
                db.query(AutomationStep)
                .filter(AutomationStep.id == step_id)
                .first()
            )
            if not step:
                raise ValueError("Automation step not found")

            step.success = success
            if error_message:
                step.error_message = error_message

            db.commit()
            db.refresh(step)

            logger.info(f"Updated step {step_id} result")
            return step
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating step result: {str(e)}")
            raise ValueError(f"Failed to update step result: {str(e)}")

    @staticmethod
    def add_automation_log(
        db: Session,
        automation_id: uuid.UUID,
        log_level: str,
        message: Optional[str] = None,
        screenshot_url: Optional[str] = None,
    ) -> AutomationLog:
        """Add log entry"""
        try:
            log = AutomationLog(
                automation_job_id=automation_id,
                log_level=log_level,
                message=message,
                screenshot_url=screenshot_url,
            )

            db.add(log)
            db.commit()
            db.refresh(log)

            logger.info(f"Added log to automation job {automation_id}")
            return log
        except Exception as e:
            db.rollback()
            logger.error(f"Error adding automation log: {str(e)}")
            raise ValueError(f"Failed to add automation log: {str(e)}")

    @staticmethod
    def get_automation_logs(
        db: Session,
        automation_id: uuid.UUID,
    ) -> list[AutomationLog]:
        """Get logs for automation job"""
        try:
            return (
                db.query(AutomationLog)
                .filter(AutomationLog.automation_job_id == automation_id)
                .order_by(AutomationLog.timestamp)
                .all()
            )
        except Exception as e:
            logger.error(f"Error retrieving logs: {str(e)}")
            raise ValueError(f"Failed to retrieve logs: {str(e)}")

    @staticmethod
    def get_automation_steps(
        db: Session,
        automation_id: uuid.UUID,
    ) -> list[AutomationStep]:
        """Get steps for automation job"""
        try:
            return (
                db.query(AutomationStep)
                .filter(AutomationStep.automation_job_id == automation_id)
                .order_by(AutomationStep.step_order)
                .all()
            )
        except Exception as e:
            logger.error(f"Error retrieving steps: {str(e)}")
            raise ValueError(f"Failed to retrieve steps: {str(e)}")
