"""
Interview session service for managing mock interviews
"""

import logging
import uuid
from datetime import datetime
from typing import Optional, Tuple

from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.interview import InterviewSession, InterviewQuestion, InterviewAnswer
from app.models.job import Job

logger = logging.getLogger(__name__)


class InterviewSessionService:
    """Service for interview session management"""

    @staticmethod
    def create_session(
        db: Session,
        user_id: uuid.UUID,
        job_id: uuid.UUID,
        session_type: str,
        difficulty_level: str = "medium",
        industry: Optional[str] = None,
        role: Optional[str] = None,
        total_questions: int = 10,
    ) -> InterviewSession:
        """Create a new interview session"""
        try:
            session = InterviewSession(
                user_id=user_id,
                job_id=job_id,
                session_type=session_type,
                difficulty_level=difficulty_level,
                industry=industry,
                role=role,
                total_questions=total_questions,
                questions_answered=0,
            )

            db.add(session)
            db.commit()
            db.refresh(session)

            logger.info(f"Created interview session for user {user_id}, type {session_type}")
            return session
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating interview session: {str(e)}")
            raise ValueError(f"Failed to create session: {str(e)}")

    @staticmethod
    def get_session(db: Session, session_id: uuid.UUID) -> Optional[InterviewSession]:
        """Get session by ID"""
        try:
            return (
                db.query(InterviewSession)
                .filter(InterviewSession.id == session_id)
                .first()
            )
        except Exception as e:
            logger.error(f"Error retrieving session: {str(e)}")
            raise ValueError(f"Failed to retrieve session: {str(e)}")

    @staticmethod
    def get_user_sessions(
        db: Session,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 20,
    ) -> Tuple[int, list[InterviewSession]]:
        """Get user's interview sessions"""
        try:
            query = db.query(InterviewSession).filter(
                InterviewSession.user_id == user_id
            )
            total = query.count()

            sessions = (
                query.order_by(desc(InterviewSession.created_at))
                .offset(skip)
                .limit(limit)
                .all()
            )

            return total, sessions
        except Exception as e:
            logger.error(f"Error retrieving sessions: {str(e)}")
            raise ValueError(f"Failed to retrieve sessions: {str(e)}")

    @staticmethod
    def complete_session(
        db: Session,
        session_id: uuid.UUID,
        overall_score: Optional[int] = None,
    ) -> InterviewSession:
        """Mark session as completed"""
        try:
            session = (
                db.query(InterviewSession)
                .filter(InterviewSession.id == session_id)
                .first()
            )
            if not session:
                raise ValueError("Session not found")

            session.completed_at = datetime.utcnow()
            session.overall_score = overall_score

            db.commit()
            db.refresh(session)

            logger.info(f"Completed session {session_id} with score {overall_score}")
            return session
        except Exception as e:
            db.rollback()
            logger.error(f"Error completing session: {str(e)}")
            raise ValueError(f"Failed to complete session: {str(e)}")

    @staticmethod
    def update_questions_answered(
        db: Session, session_id: uuid.UUID, count: int
    ) -> InterviewSession:
        """Update count of answered questions"""
        try:
            session = (
                db.query(InterviewSession)
                .filter(InterviewSession.id == session_id)
                .first()
            )
            if not session:
                raise ValueError("Session not found")

            session.questions_answered = count
            db.commit()
            db.refresh(session)

            return session
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating answered count: {str(e)}")
            raise ValueError(f"Failed to update answered count: {str(e)}")

    @staticmethod
    def delete_session(db: Session, session_id: uuid.UUID) -> None:
        """Delete a session"""
        try:
            session = (
                db.query(InterviewSession)
                .filter(InterviewSession.id == session_id)
                .first()
            )
            if not session:
                raise ValueError("Session not found")

            db.delete(session)
            db.commit()

            logger.info(f"Deleted session {session_id}")
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting session: {str(e)}")
            raise ValueError(f"Failed to delete session: {str(e)}")
