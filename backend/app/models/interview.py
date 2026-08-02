"""
Interview coaching models for AI-powered interview preparation
"""

from datetime import datetime
import uuid
from typing import Optional
from decimal import Decimal

from sqlalchemy import String, Integer, DateTime, ForeignKey, func, Text, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class InterviewSession(Base):
    """Mock interview sessions"""

    __tablename__ = "interview_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    session_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    difficulty_level: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    industry: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    role: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    total_questions: Mapped[Optional[int]] = mapped_column(Integer(), nullable=True)
    questions_answered: Mapped[int] = mapped_column(Integer(), nullable=False, default=0)

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    overall_score: Mapped[Optional[int]] = mapped_column(Integer(), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    questions = relationship(
        "InterviewQuestion",
        back_populates="session",
        cascade="all, delete-orphan",
        foreign_keys="InterviewQuestion.session_id",
    )

    def __repr__(self) -> str:
        return f"<InterviewSession(user_id={self.user_id}, session_type={self.session_type}, score={self.overall_score})>"


class InterviewQuestion(Base):
    """Interview questions for sessions"""

    __tablename__ = "interview_questions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("interview_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    question_text: Mapped[str] = mapped_column(Text(), nullable=False)
    question_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    question_order: Mapped[int] = mapped_column(Integer(), nullable=False)
    time_limit_seconds: Mapped[Optional[int]] = mapped_column(Integer(), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    session = relationship("InterviewSession", back_populates="questions")
    answer = relationship(
        "InterviewAnswer",
        back_populates="question",
        uselist=False,
        cascade="all, delete-orphan",
        foreign_keys="InterviewAnswer.question_id",
    )

    def __repr__(self) -> str:
        return f"<InterviewQuestion(session_id={self.session_id}, order={self.question_order})>"


class InterviewAnswer(Base):
    """User answers to interview questions"""

    __tablename__ = "interview_answers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    question_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("interview_questions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    user_answer: Mapped[Optional[str]] = mapped_column(Text(), nullable=True)
    answer_time_seconds: Mapped[Optional[int]] = mapped_column(Integer(), nullable=True)
    score: Mapped[Optional[int]] = mapped_column(Integer(), nullable=True)
    feedback: Mapped[Optional[str]] = mapped_column(Text(), nullable=True)
    strengths: Mapped[Optional[str]] = mapped_column(Text(), nullable=True)
    improvements: Mapped[Optional[str]] = mapped_column(Text(), nullable=True)
    ai_model: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    question = relationship("InterviewQuestion", back_populates="answer")

    def __repr__(self) -> str:
        return f"<InterviewAnswer(question_id={self.question_id}, score={self.score})>"


class InterviewTip(Base):
    """Interview tips and resources"""

    __tablename__ = "interview_tips"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    tip_text: Mapped[str] = mapped_column(Text(), nullable=False)
    tip_order: Mapped[Optional[int]] = mapped_column(Integer(), nullable=True)
    helpful_count: Mapped[int] = mapped_column(Integer(), nullable=False, default=0)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<InterviewTip(user_id={self.user_id}, category={self.category})>"


class InterviewMetrics(Base):
    """User interview performance metrics"""

    __tablename__ = "interview_metrics"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        unique=True,
    )

    average_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    total_sessions: Mapped[int] = mapped_column(Integer(), nullable=False, default=0)
    total_questions: Mapped[int] = mapped_column(Integer(), nullable=False, default=0)
    strongest_category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    weakest_category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    improvement_rate: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)

    last_updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<InterviewMetrics(user_id={self.user_id}, avg_score={self.average_score})>"
