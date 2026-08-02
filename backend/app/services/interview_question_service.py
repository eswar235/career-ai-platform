"""
Interview question service
"""

import logging
import uuid
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.interview import InterviewQuestion, InterviewAnswer

logger = logging.getLogger(__name__)


class InterviewQuestionService:
    """Service for managing interview questions"""

    @staticmethod
    def create_question(
        db: Session,
        session_id: uuid.UUID,
        question_text: str,
        question_order: int,
        question_type: Optional[str] = None,
        category: Optional[str] = None,
        time_limit_seconds: Optional[int] = None,
    ) -> InterviewQuestion:
        """Create a new question"""
        try:
            question = InterviewQuestion(
                session_id=session_id,
                question_text=question_text,
                question_order=question_order,
                question_type=question_type,
                category=category,
                time_limit_seconds=time_limit_seconds,
            )

            db.add(question)
            db.commit()
            db.refresh(question)

            logger.info(f"Created question for session {session_id}")
            return question
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating question: {str(e)}")
            raise ValueError(f"Failed to create question: {str(e)}")

    @staticmethod
    def get_question(db: Session, question_id: uuid.UUID) -> Optional[InterviewQuestion]:
        """Get question by ID"""
        try:
            return (
                db.query(InterviewQuestion)
                .filter(InterviewQuestion.id == question_id)
                .first()
            )
        except Exception as e:
            logger.error(f"Error retrieving question: {str(e)}")
            raise ValueError(f"Failed to retrieve question: {str(e)}")

    @staticmethod
    def get_session_questions(
        db: Session, session_id: uuid.UUID
    ) -> list[InterviewQuestion]:
        """Get all questions for a session"""
        try:
            return (
                db.query(InterviewQuestion)
                .filter(InterviewQuestion.session_id == session_id)
                .order_by(InterviewQuestion.question_order)
                .all()
            )
        except Exception as e:
            logger.error(f"Error retrieving questions: {str(e)}")
            raise ValueError(f"Failed to retrieve questions: {str(e)}")

    @staticmethod
    def get_next_unanswered_question(
        db: Session, session_id: uuid.UUID
    ) -> Optional[InterviewQuestion]:
        """Get next unanswered question"""
        try:
            questions = InterviewQuestionService.get_session_questions(db, session_id)
            for q in questions:
                if not q.answer or not q.answer.user_answer:
                    return q
            return None
        except Exception as e:
            logger.error(f"Error getting next question: {str(e)}")
            raise ValueError(f"Failed to get next question: {str(e)}")

    @staticmethod
    def bulk_create_questions(
        db: Session,
        session_id: uuid.UUID,
        questions_data: list[dict],
    ) -> list[InterviewQuestion]:
        """Create multiple questions at once"""
        try:
            questions = []
            for data in questions_data:
                question = InterviewQuestion(
                    session_id=session_id,
                    question_text=data["text"],
                    question_order=data["order"],
                    question_type=data.get("type"),
                    category=data.get("category"),
                    time_limit_seconds=data.get("time_limit"),
                )
                questions.append(question)

            db.add_all(questions)
            db.commit()

            for q in questions:
                db.refresh(q)

            logger.info(f"Created {len(questions)} questions for session {session_id}")
            return questions
        except Exception as e:
            db.rollback()
            logger.error(f"Error bulk creating questions: {str(e)}")
            raise ValueError(f"Failed to create questions: {str(e)}")
