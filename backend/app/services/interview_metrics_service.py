"""
Interview metrics and performance tracking service
"""

import logging
import uuid
from typing import Optional
from decimal import Decimal

from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.models.interview import InterviewMetrics, InterviewSession, InterviewAnswer

logger = logging.getLogger(__name__)


class InterviewMetricsService:
    """Service for tracking interview performance metrics"""

    @staticmethod
    def get_or_create_metrics(db: Session, user_id: uuid.UUID) -> InterviewMetrics:
        """Get or create metrics for user"""
        try:
            metrics = (
                db.query(InterviewMetrics)
                .filter(InterviewMetrics.user_id == user_id)
                .first()
            )
            if not metrics:
                metrics = InterviewMetrics(user_id=user_id)
                db.add(metrics)
                db.commit()
                db.refresh(metrics)

            return metrics
        except Exception as e:
            logger.error(f"Error getting metrics: {str(e)}")
            raise ValueError(f"Failed to get metrics: {str(e)}")

    @staticmethod
    def update_metrics(db: Session, user_id: uuid.UUID) -> InterviewMetrics:
        """Recalculate metrics for user"""
        try:
            metrics = InterviewMetricsService.get_or_create_metrics(db, user_id)

            # Get all sessions for user
            sessions = (
                db.query(InterviewSession)
                .filter(InterviewSession.user_id == user_id)
                .filter(InterviewSession.completed_at.isnot(None))
                .all()
            )

            metrics.total_sessions = len(sessions)

            # Calculate average score
            scores = [s.overall_score for s in sessions if s.overall_score]
            if scores:
                metrics.average_score = Decimal(sum(scores) / len(scores))

            # Count total questions
            total_q = (
                db.query(func.count(InterviewAnswer.id))
                .join(InterviewSession, 
                     InterviewAnswer.question_id == InterviewSession.id)
                .filter(InterviewSession.user_id == user_id)
                .scalar()
            )
            metrics.total_questions = total_q or 0

            # Find strongest/weakest categories
            category_scores = {}
            for session in sessions:
                for q in session.questions:
                    if q.answer and q.answer.score:
                        cat = q.category or "general"
                        if cat not in category_scores:
                            category_scores[cat] = []
                        category_scores[cat].append(q.answer.score)

            if category_scores:
                avg_by_cat = {
                    cat: sum(scores) / len(scores)
                    for cat, scores in category_scores.items()
                }
                metrics.strongest_category = max(avg_by_cat, key=avg_by_cat.get)
                metrics.weakest_category = min(avg_by_cat, key=avg_by_cat.get)

            # Calculate improvement rate
            if len(scores) > 1:
                improvement = (scores[-1] - scores[0]) / scores[0] * 100
                metrics.improvement_rate = Decimal(improvement)

            db.commit()
            db.refresh(metrics)

            logger.info(f"Updated metrics for user {user_id}")
            return metrics
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating metrics: {str(e)}")
            raise ValueError(f"Failed to update metrics: {str(e)}")

    @staticmethod
    def get_metrics(db: Session, user_id: uuid.UUID) -> Optional[InterviewMetrics]:
        """Get user metrics"""
        try:
            return (
                db.query(InterviewMetrics)
                .filter(InterviewMetrics.user_id == user_id)
                .first()
            )
        except Exception as e:
            logger.error(f"Error retrieving metrics: {str(e)}")
            raise ValueError(f"Failed to retrieve metrics: {str(e)}")
