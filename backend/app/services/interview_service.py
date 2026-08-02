"""
Interview service for managing interviews
"""

import logging
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.application import Interview, ApplicationActivity

logger = logging.getLogger(__name__)


class InterviewService:
    """Service for interview management"""

    @staticmethod
    def create_interview(
        db: Session,
        application_id: uuid.UUID,
        interview_type: Optional[str] = None,
        scheduled_date: Optional[datetime] = None,
        duration_minutes: Optional[int] = None,
        interviewer_name: Optional[str] = None,
        interviewer_email: Optional[str] = None,
        meeting_link: Optional[str] = None,
        preparation_notes: Optional[str] = None,
    ) -> Interview:
        """Create a new interview"""
        try:
            interview = Interview(
                application_id=application_id,
                interview_type=interview_type,
                scheduled_date=scheduled_date,
                duration_minutes=duration_minutes,
                interviewer_name=interviewer_name,
                interviewer_email=interviewer_email,
                meeting_link=meeting_link,
                preparation_notes=preparation_notes,
                status="scheduled",
            )

            db.add(interview)
            db.commit()
            db.refresh(interview)

            # Log activity
            InterviewService._log_activity(
                db,
                application_id,
                "interview_scheduled",
                f"Interview scheduled: {interview_type}",
            )

            logger.info(f"Created interview for application {application_id}")
            return interview
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating interview: {str(e)}")
            raise ValueError(f"Failed to create interview: {str(e)}")

    @staticmethod
    def get_interview(
        db: Session,
        interview_id: uuid.UUID,
    ) -> Optional[Interview]:
        """Get an interview by ID"""
        try:
            return db.query(Interview).filter(Interview.id == interview_id).first()
        except Exception as e:
            logger.error(f"Error retrieving interview: {str(e)}")
            raise ValueError(f"Failed to retrieve interview: {str(e)}")

    @staticmethod
    def get_application_interviews(
        db: Session,
        application_id: uuid.UUID,
    ) -> list[Interview]:
        """Get all interviews for an application"""
        try:
            return (
                db.query(Interview)
                .filter(Interview.application_id == application_id)
                .order_by(desc(Interview.scheduled_date))
                .all()
            )
        except Exception as e:
            logger.error(f"Error retrieving interviews: {str(e)}")
            raise ValueError(f"Failed to retrieve interviews: {str(e)}")

    @staticmethod
    def update_interview(
        db: Session,
        interview_id: uuid.UUID,
        interview_type: Optional[str] = None,
        scheduled_date: Optional[datetime] = None,
        duration_minutes: Optional[int] = None,
        interviewer_name: Optional[str] = None,
        interviewer_email: Optional[str] = None,
        meeting_link: Optional[str] = None,
        preparation_notes: Optional[str] = None,
        status: Optional[str] = None,
        feedback: Optional[str] = None,
        interview_score: Optional[int] = None,
    ) -> Interview:
        """Update an interview"""
        try:
            interview = db.query(Interview).filter(Interview.id == interview_id).first()
            if not interview:
                raise ValueError("Interview not found")

            if interview_type is not None:
                interview.interview_type = interview_type
            if scheduled_date is not None:
                interview.scheduled_date = scheduled_date
            if duration_minutes is not None:
                interview.duration_minutes = duration_minutes
            if interviewer_name is not None:
                interview.interviewer_name = interviewer_name
            if interviewer_email is not None:
                interview.interviewer_email = interviewer_email
            if meeting_link is not None:
                interview.meeting_link = meeting_link
            if preparation_notes is not None:
                interview.preparation_notes = preparation_notes
            if status is not None:
                interview.status = status
            if feedback is not None:
                interview.feedback = feedback
            if interview_score is not None:
                interview.interview_score = interview_score

            db.commit()
            db.refresh(interview)

            # Log if completed
            if status == "completed":
                InterviewService._log_activity(
                    db,
                    interview.application_id,
                    "interview_completed",
                    f"Interview completed with score {interview_score}",
                )

            logger.info(f"Updated interview {interview_id}")
            return interview
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating interview: {str(e)}")
            raise ValueError(f"Failed to update interview: {str(e)}")

    @staticmethod
    def delete_interview(
        db: Session,
        interview_id: uuid.UUID,
    ) -> None:
        """Delete an interview"""
        try:
            interview = db.query(Interview).filter(Interview.id == interview_id).first()
            if not interview:
                raise ValueError("Interview not found")

            application_id = interview.application_id
            db.delete(interview)
            db.commit()

            InterviewService._log_activity(
                db, application_id, "interview_deleted", "Interview cancelled"
            )

            logger.info(f"Deleted interview {interview_id}")
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting interview: {str(e)}")
            raise ValueError(f"Failed to delete interview: {str(e)}")

    @staticmethod
    def _log_activity(
        db: Session,
        application_id: uuid.UUID,
        activity_type: str,
        description: Optional[str] = None,
    ) -> None:
        """Log an activity"""
        try:
            activity = ApplicationActivity(
                application_id=application_id,
                activity_type=activity_type,
                description=description,
            )
            db.add(activity)
            db.commit()
        except Exception as e:
            logger.warning(f"Failed to log activity: {str(e)}")
