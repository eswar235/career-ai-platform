"""
Interview coaching API routes
"""

import logging
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Query

from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.interview import (
    InterviewSessionCreate,
    InterviewSessionResponse,
    InterviewSessionDetailResponse,
    InterviewQuestionResponse,
    InterviewAnswerCreate,
    InterviewAnswerResponse,
    InterviewMetricsResponse,
    SessionResultsResponse,
)
from app.services.interview_session_service import InterviewSessionService
from app.services.interview_question_service import InterviewQuestionService
from app.services.interview_answer_service import InterviewAnswerService
from app.services.interview_metrics_service import InterviewMetricsService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/interviews", tags=["interviews"])


@router.post("", response_model=InterviewSessionResponse)
def create_session(
    request: InterviewSessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create new interview session"""
    try:
        session = InterviewSessionService.create_session(
            db=db,
            user_id=current_user.id,
            job_id=request.job_id,
            session_type=request.session_type,
            difficulty_level=request.difficulty_level,
            industry=request.industry,
            role=request.role,
            total_questions=request.num_questions,
        )
        return session
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating session: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                          detail="Failed to create session")


@router.get("/{session_id}", response_model=InterviewSessionDetailResponse)
def get_session(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get interview session details"""
    try:
        session = InterviewSessionService.get_session(db, session_id)
        if not session or session.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                              detail="Session not found")
        return session
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving session: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                          detail="Failed to retrieve session")


@router.get("", response_model=list[InterviewSessionResponse])
def list_sessions(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List user's interview sessions"""
    try:
        total, sessions = InterviewSessionService.get_user_sessions(
            db, current_user.id, skip, limit
        )
        return sessions
    except Exception as e:
        logger.error(f"Error listing sessions: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                          detail="Failed to list sessions")


@router.get("/{session_id}/questions", response_model=list[InterviewQuestionResponse])
def get_questions(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get questions for a session"""
    try:
        session = InterviewSessionService.get_session(db, session_id)
        if not session or session.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                              detail="Session not found")

        questions = InterviewQuestionService.get_session_questions(db, session_id)
        return questions
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving questions: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                          detail="Failed to retrieve questions")


@router.post("/{question_id}/answer", response_model=InterviewAnswerResponse)
def submit_answer(
    question_id: uuid.UUID,
    request: InterviewAnswerCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Submit answer to question"""
    try:
        answer = InterviewAnswerService.submit_answer(
            db=db,
            question_id=question_id,
            user_answer=request.user_answer,
            answer_time_seconds=request.answer_time_seconds,
        )

        # Evaluate answer
        question = InterviewQuestionService.get_question(db, question_id)
        answer = InterviewAnswerService.evaluate_answer(
            db, answer.id, question.question_text
        )

        return answer
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error submitting answer: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                          detail="Failed to submit answer")


@router.post("/{session_id}/complete", response_model=SessionResultsResponse)
def complete_session(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Complete interview session"""
    try:
        session = InterviewSessionService.get_session(db, session_id)
        if not session or session.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                              detail="Session not found")

        # Calculate overall score
        answers = InterviewAnswerService.get_session_answers(db, session_id)
        scores = [a.score for a in answers if a.score]
        overall_score = int(sum(scores) / len(scores)) if scores else 0

        session = InterviewSessionService.complete_session(
            db, session_id, overall_score
        )

        # Update metrics
        InterviewMetricsService.update_metrics(db, current_user.id)

        # Build results
        category_scores = {}
        for answer in answers:
            question = answer.question
            cat = question.category or "general"
            if cat not in category_scores:
                category_scores[cat] = []
            if answer.score:
                category_scores[cat].append(answer.score)

        category_avgs = {cat: int(sum(s) / len(s)) for cat, s in category_scores.items()}

        strengths = set()
        improvements = set()
        for answer in answers:
            if answer.strengths:
                strengths.update(answer.strengths.split(","))
            if answer.improvements:
                improvements.update(answer.improvements.split(","))

        return SessionResultsResponse(
            session_id=session_id,
            overall_score=overall_score,
            total_questions=session.total_questions or 0,
            questions_answered=len(answers),
            duration_seconds=int((session.completed_at - session.started_at).total_seconds()),
            category_scores=category_avgs,
            strengths=list(strengths)[:5],
            improvements=list(improvements)[:5],
            next_steps=["Practice weak areas", "Review technical concepts"],
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error completing session: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                          detail="Failed to complete session")


@router.get("/metrics/performance", response_model=InterviewMetricsResponse)
def get_metrics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get user performance metrics"""
    try:
        metrics = InterviewMetricsService.get_metrics(db, current_user.id)
        if not metrics:
            metrics = InterviewMetricsService.get_or_create_metrics(db, current_user.id)
        return metrics
    except Exception as e:
        logger.error(f"Error retrieving metrics: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                          detail="Failed to retrieve metrics")
