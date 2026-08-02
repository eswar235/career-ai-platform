"""
Job Alert Service - Manage job alerts and matching
"""

import logging
import uuid
from typing import Tuple, List, Optional
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.notification import JobAlert, AlertJobMatch
from app.models.job import Job
from app.models.user import User

logger = logging.getLogger(__name__)


class JobAlertService:
    """Job alert service"""

    @staticmethod
    def create_or_get_alert(
        db: Session,
        user_id: uuid.UUID,
        keywords: Optional[str] = None,
        locations: Optional[List[str]] = None,
        job_titles: Optional[List[str]] = None,
        experience_levels: Optional[List[str]] = None,
        salary_min: Optional[int] = None,
        salary_max: Optional[int] = None,
        min_match_score: float = 60,
        notification_frequency: str = "daily",
        preferred_time: Optional[str] = None,
    ) -> JobAlert:
        """Create or update job alert"""
        try:
            alert = db.query(JobAlert).filter(JobAlert.user_id == user_id).first()

            if alert:
                alert.keywords = keywords
                alert.locations = locations
                alert.job_titles = job_titles
                alert.experience_levels = experience_levels
                alert.salary_min = salary_min
                alert.salary_max = salary_max
                alert.min_match_score = min_match_score
                alert.notification_frequency = notification_frequency
                alert.preferred_time = preferred_time
                alert.updated_at = datetime.utcnow()
            else:
                alert = JobAlert(
                    user_id=user_id,
                    keywords=keywords,
                    locations=locations,
                    job_titles=job_titles,
                    experience_levels=experience_levels,
                    salary_min=salary_min,
                    salary_max=salary_max,
                    min_match_score=min_match_score,
                    notification_frequency=notification_frequency,
                    preferred_time=preferred_time,
                    is_active=True,
                )
                db.add(alert)

            db.commit()
            db.refresh(alert)
            logger.info(f"Alert created/updated for user {user_id}")
            return alert

        except Exception as e:
            logger.error(f"Error creating/updating alert: {str(e)}")
            db.rollback()
            raise

    @staticmethod
    def get_alert(db: Session, user_id: uuid.UUID) -> Optional[JobAlert]:
        """Get user's job alert"""
        try:
            return db.query(JobAlert).filter(JobAlert.user_id == user_id).first()
        except Exception as e:
            logger.error(f"Error retrieving alert: {str(e)}")
            raise

    @staticmethod
    def update_alert(
        db: Session,
        user_id: uuid.UUID,
        **kwargs,
    ) -> JobAlert:
        """Update job alert"""
        try:
            alert = db.query(JobAlert).filter(JobAlert.user_id == user_id).first()
            if not alert:
                raise ValueError(f"Alert not found for user {user_id}")

            for key, value in kwargs.items():
                if hasattr(alert, key):
                    setattr(alert, key, value)

            alert.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(alert)
            logger.info(f"Alert updated for user {user_id}")
            return alert

        except Exception as e:
            logger.error(f"Error updating alert: {str(e)}")
            db.rollback()
            raise

    @staticmethod
    def toggle_alert(db: Session, user_id: uuid.UUID, is_active: bool) -> JobAlert:
        """Toggle alert on/off"""
        try:
            alert = db.query(JobAlert).filter(JobAlert.user_id == user_id).first()
            if not alert:
                raise ValueError(f"Alert not found for user {user_id}")

            alert.is_active = is_active
            alert.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(alert)
            logger.info(f"Alert toggled to {is_active} for user {user_id}")
            return alert

        except Exception as e:
            logger.error(f"Error toggling alert: {str(e)}")
            db.rollback()
            raise

    @staticmethod
    def find_matching_jobs(
        db: Session,
        alert: JobAlert,
        match_score_threshold: float = 60.0,
    ) -> List[Tuple[Job, float]]:
        """Find jobs matching alert criteria"""
        try:
            query = db.query(Job).filter(Job.is_active == True)

            # Apply filters
            if alert.keywords:
                keywords_lower = alert.keywords.lower()
                query = query.filter(
                    or_(
                        Job.title.ilike(f"%{keywords_lower}%"),
                        Job.description.ilike(f"%{keywords_lower}%"),
                        Job.requirements.ilike(f"%{keywords_lower}%"),
                    )
                )

            if alert.locations:
                query = query.filter(Job.location.in_(alert.locations))

            if alert.job_titles:
                query = query.filter(Job.title.in_(alert.job_titles))

            if alert.experience_levels:
                query = query.filter(Job.experience_level.in_(alert.experience_levels))

            if alert.salary_min:
                query = query.filter(
                    or_(
                        Job.salary_min >= alert.salary_min,
                        Job.salary_max >= alert.salary_min,
                    )
                )

            if alert.salary_max:
                query = query.filter(
                    or_(
                        Job.salary_min <= alert.salary_max,
                        Job.salary_max <= alert.salary_max,
                    )
                )

            jobs = query.all()
            logger.info(f"Found {len(jobs)} matching jobs for alert {alert.id}")
            return jobs

        except Exception as e:
            logger.error(f"Error finding matching jobs: {str(e)}")
            raise

    @staticmethod
    def record_match(
        db: Session,
        alert_id: uuid.UUID,
        job_id: uuid.UUID,
        match_score: float,
    ) -> AlertJobMatch:
        """Record alert-job match"""
        try:
            match = db.query(AlertJobMatch).filter(
                and_(
                    AlertJobMatch.alert_id == alert_id,
                    AlertJobMatch.job_id == job_id,
                )
            ).first()

            if match:
                logger.info(f"Match already exists for alert {alert_id} and job {job_id}")
                return match

            match = AlertJobMatch(
                alert_id=alert_id,
                job_id=job_id,
                match_score=match_score,
                notification_sent=False,
                user_dismissed=False,
            )
            db.add(match)
            db.commit()
            db.refresh(match)
            logger.info(f"Match recorded for alert {alert_id} and job {job_id}")
            return match

        except Exception as e:
            logger.error(f"Error recording match: {str(e)}")
            db.rollback()
            raise

    @staticmethod
    def mark_notification_sent(
        db: Session,
        match_id: uuid.UUID,
    ) -> AlertJobMatch:
        """Mark notification as sent"""
        try:
            match = db.query(AlertJobMatch).filter(AlertJobMatch.id == match_id).first()
            if not match:
                raise ValueError(f"Match not found: {match_id}")

            match.notification_sent = True
            db.commit()
            db.refresh(match)
            logger.info(f"Notification marked as sent for match {match_id}")
            return match

        except Exception as e:
            logger.error(f"Error marking notification sent: {str(e)}")
            db.rollback()
            raise

    @staticmethod
    def dismiss_match(
        db: Session,
        match_id: uuid.UUID,
    ) -> AlertJobMatch:
        """Dismiss job match"""
        try:
            match = db.query(AlertJobMatch).filter(AlertJobMatch.id == match_id).first()
            if not match:
                raise ValueError(f"Match not found: {match_id}")

            match.user_dismissed = True
            db.commit()
            db.refresh(match)
            logger.info(f"Match dismissed {match_id}")
            return match

        except Exception as e:
            logger.error(f"Error dismissing match: {str(e)}")
            db.rollback()
            raise

    @staticmethod
    def get_unsent_matches(
        db: Session,
        alert_id: uuid.UUID,
    ) -> List[AlertJobMatch]:
        """Get unsent notification matches"""
        try:
            matches = db.query(AlertJobMatch).filter(
                and_(
                    AlertJobMatch.alert_id == alert_id,
                    AlertJobMatch.notification_sent == False,
                    AlertJobMatch.user_dismissed == False,
                )
            ).all()
            logger.info(f"Found {len(matches)} unsent matches for alert {alert_id}")
            return matches

        except Exception as e:
            logger.error(f"Error getting unsent matches: {str(e)}")
            raise

    @staticmethod
    def get_user_matches(
        db: Session,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 20,
    ) -> Tuple[int, List[AlertJobMatch]]:
        """Get user's alert matches"""
        try:
            query = db.query(AlertJobMatch).join(
                JobAlert, AlertJobMatch.alert_id == JobAlert.id
            ).filter(JobAlert.user_id == user_id)

            total = query.count()
            matches = query.offset(skip).limit(limit).all()
            logger.info(f"Retrieved {len(matches)} matches for user {user_id}")
            return total, matches

        except Exception as e:
            logger.error(f"Error getting user matches: {str(e)}")
            raise
