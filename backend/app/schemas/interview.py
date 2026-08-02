"""
Pydantic schemas for interview coaching
"""

from datetime import datetime
from typing import Optional
from decimal import Decimal
import uuid

from pydantic import BaseModel, Field


# ========== Interview Session Schemas ==========

class InterviewSessionBase(BaseModel):
    """Base session schema"""

    session_type: str = Field(..., description="technical, behavioral, general")
    difficulty_level: str = Field("medium", description="easy, medium, hard")
    industry: Optional[str] = Field(None, description="Industry for questions")
    role: Optional[str] = Field(None, description="Job role")


class InterviewSessionCreate(BaseModel):
    """Create session request"""

    job_id: uuid.UUID = Field(..., description="Associated job")
    session_type: str = Field(..., description="Interview type")
    difficulty_level: str = Field("medium", description="Difficulty level")
    industry: Optional[str] = Field(None)
    role: Optional[str] = Field(None)
    num_questions: int = Field(10, ge=1, le=50, description="Number of questions")


class InterviewSessionResponse(BaseModel):
    """Session response"""

    id: uuid.UUID
    user_id: uuid.UUID
    job_id: uuid.UUID
    session_type: Optional[str]
    difficulty_level: Optional[str]
    industry: Optional[str]
    role: Optional[str]
    total_questions: Optional[int]
    questions_answered: int
    overall_score: Optional[int]
    started_at: datetime
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class InterviewSessionDetailResponse(InterviewSessionResponse):
    """Detailed session with questions"""

    questions: list["InterviewQuestionResponse"] = Field(default_factory=list)

    class Config:
        from_attributes = True


# ========== Interview Question Schemas ==========

class InterviewQuestionResponse(BaseModel):
    """Question response"""

    id: uuid.UUID
    session_id: uuid.UUID
    question_text: str
    question_type: Optional[str]
    category: Optional[str]
    question_order: int
    time_limit_seconds: Optional[int]
    created_at: datetime
    answer: Optional["InterviewAnswerResponse"] = None

    class Config:
        from_attributes = True


# ========== Interview Answer Schemas ==========

class InterviewAnswerCreate(BaseModel):
    """Submit answer request"""

    user_answer: str = Field(..., description="User's answer text")
    answer_time_seconds: Optional[int] = Field(None, description="Time taken")


class InterviewAnswerResponse(BaseModel):
    """Answer response"""

    id: uuid.UUID
    question_id: uuid.UUID
    user_answer: Optional[str]
    answer_time_seconds: Optional[int]
    score: Optional[int]
    feedback: Optional[str]
    strengths: Optional[str]
    improvements: Optional[str]
    ai_model: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ========== Interview Tips Schemas ==========

class InterviewTipCreate(BaseModel):
    """Create tip request"""

    category: str = Field(..., description="Tip category")
    tip_text: str = Field(..., description="Tip content")
    tip_order: Optional[int] = Field(None, description="Display order")


class InterviewTipResponse(BaseModel):
    """Tip response"""

    id: uuid.UUID
    user_id: uuid.UUID
    category: Optional[str]
    tip_text: str
    tip_order: Optional[int]
    helpful_count: int
    created_at: datetime

    class Config:
        from_attributes = True


# ========== Interview Metrics Schemas ==========

class InterviewMetricsResponse(BaseModel):
    """Performance metrics response"""

    id: uuid.UUID
    user_id: uuid.UUID
    average_score: Optional[Decimal]
    total_sessions: int
    total_questions: int
    strongest_category: Optional[str]
    weakest_category: Optional[str]
    improvement_rate: Optional[Decimal]
    last_updated: datetime

    class Config:
        from_attributes = True


# ========== Session Control Schemas ==========

class CompleteSessionRequest(BaseModel):
    """Request to complete session"""

    session_id: uuid.UUID = Field(..., description="Session to complete")


class SessionResultsResponse(BaseModel):
    """Session results/summary"""

    session_id: uuid.UUID
    overall_score: int
    total_questions: int
    questions_answered: int
    duration_seconds: int
    category_scores: dict[str, int]
    strengths: list[str]
    improvements: list[str]
    next_steps: list[str]


class QuestionFeedbackResponse(BaseModel):
    """Feedback for single question"""

    question_id: uuid.UUID
    score: int
    feedback: str
    strengths: list[str]
    improvements: list[str]
    best_answer: Optional[str]


# ========== Bulk Schemas ==========

class GenerateQuestionsRequest(BaseModel):
    """Generate questions request"""

    job_id: uuid.UUID = Field(...)
    session_type: str = Field(..., description="Interview type")
    difficulty_level: str = Field("medium")
    num_questions: int = Field(10, ge=1, le=50)
    industry: Optional[str] = Field(None)


class QuestionBankResponse(BaseModel):
    """Question bank response"""

    total_questions: int
    by_type: dict[str, int]
    by_category: dict[str, int]
    by_difficulty: dict[str, int]


# ========== Coaching Schemas ==========

class CoachingTipsRequest(BaseModel):
    """Request coaching tips"""

    category: str = Field(..., description="Tip category")
    difficulty_level: Optional[str] = Field(None)
    count: int = Field(5, ge=1, le=20)


class ProgressReportResponse(BaseModel):
    """User progress report"""

    total_sessions: int
    average_score: float
    best_score: int
    worst_score: int
    categories_covered: list[str]
    recommended_focus: list[str]
    estimated_readiness: int  # 0-100
