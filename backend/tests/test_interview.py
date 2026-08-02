"""
Interview Coaching Tests
"""

import uuid
from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.models.interview import (
    InterviewSession,
    InterviewQuestion,
    InterviewAnswer,
    InterviewTip,
    InterviewMetrics,
)
from app.schemas.interview import InterviewSessionCreate
from app.services.interview_session_service import InterviewSessionService
from app.services.interview_question_service import InterviewQuestionService
from app.services.interview_answer_service import InterviewAnswerService
from app.services.interview_metrics_service import InterviewMetricsService


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def test_user(db_session):
    """Create test user"""
    from app.models.user import User
    user = User(
        email=f"test_{uuid.uuid4()}@example.com",
        password_hash="hashed_password",
        full_name="Test User",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def test_job(db_session, test_user):
    """Create test job"""
    from app.models.job import Job
    job = Job(
        title="Software Engineer",
        company="Test Company",
        url="https://example.com/job",
        salary_min=100000,
        salary_max=150000,
        location="San Francisco, CA",
        job_type="Full-time",
        description="Test job description",
    )
    db_session.add(job)
    db_session.commit()
    return job


class TestInterviewSessionService:
    """Interview Session Service Tests"""

    def test_create_session(self, db_session, test_user, test_job):
        """Test creating interview session"""
        session = InterviewSessionService.create_session(
            db=db_session,
            user_id=test_user.id,
            job_id=test_job.id,
            session_type="technical",
            difficulty_level="medium",
            industry="tech",
            role="backend",
            total_questions=5,
        )

        assert session is not None
        assert session.user_id == test_user.id
        assert session.job_id == test_job.id
        assert session.session_type == "technical"
        assert session.difficulty_level == "medium"
        assert session.total_questions == 5
        assert session.started_at is not None

    def test_get_session(self, db_session, test_user, test_job):
        """Test retrieving interview session"""
        created = InterviewSessionService.create_session(
            db=db_session,
            user_id=test_user.id,
            job_id=test_job.id,
            session_type="behavioral",
            total_questions=3,
        )

        retrieved = InterviewSessionService.get_session(db_session, created.id)

        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.user_id == test_user.id

    def test_get_user_sessions(self, db_session, test_user, test_job):
        """Test listing user sessions"""
        # Create multiple sessions
        for i in range(3):
            InterviewSessionService.create_session(
                db=db_session,
                user_id=test_user.id,
                job_id=test_job.id,
                session_type="technical",
                total_questions=5,
            )

        total, sessions = InterviewSessionService.get_user_sessions(
            db_session, test_user.id, skip=0, limit=20
        )

        assert total == 3
        assert len(sessions) == 3

    def test_complete_session(self, db_session, test_user, test_job):
        """Test completing interview session"""
        session = InterviewSessionService.create_session(
            db=db_session,
            user_id=test_user.id,
            job_id=test_job.id,
            session_type="general",
            total_questions=2,
        )

        completed = InterviewSessionService.complete_session(
            db_session, session.id, overall_score=85
        )

        assert completed.overall_score == 85
        assert completed.completed_at is not None


class TestInterviewQuestionService:
    """Interview Question Service Tests"""

    def test_generate_questions(self, db_session, test_user, test_job):
        """Test generating interview questions"""
        session = InterviewSessionService.create_session(
            db=db_session,
            user_id=test_user.id,
            job_id=test_job.id,
            session_type="technical",
            difficulty_level="hard",
            industry="tech",
            role="backend",
            total_questions=3,
        )

        questions = InterviewQuestionService.generate_questions(
            db=db_session,
            session_id=session.id,
            session_type="technical",
            difficulty_level="hard",
            industry="tech",
            role="backend",
            num_questions=3,
        )

        assert len(questions) == 3
        assert all(q.session_id == session.id for q in questions)
        assert all(q.question_text for q in questions)

    def test_get_session_questions(self, db_session, test_user, test_job):
        """Test retrieving session questions"""
        session = InterviewSessionService.create_session(
            db=db_session,
            user_id=test_user.id,
            job_id=test_job.id,
            session_type="behavioral",
            total_questions=2,
        )

        InterviewQuestionService.generate_questions(
            db=db_session,
            session_id=session.id,
            session_type="behavioral",
            num_questions=2,
        )

        questions = InterviewQuestionService.get_session_questions(
            db_session, session.id
        )

        assert len(questions) == 2
        assert all(q.session_id == session.id for q in questions)

    def test_get_question(self, db_session, test_user, test_job):
        """Test retrieving single question"""
        session = InterviewSessionService.create_session(
            db=db_session,
            user_id=test_user.id,
            job_id=test_job.id,
            session_type="general",
            total_questions=1,
        )

        questions = InterviewQuestionService.generate_questions(
            db=db_session,
            session_id=session.id,
            session_type="general",
            num_questions=1,
        )

        retrieved = InterviewQuestionService.get_question(
            db_session, questions[0].id
        )

        assert retrieved is not None
        assert retrieved.id == questions[0].id
        assert retrieved.question_text == questions[0].question_text


class TestInterviewAnswerService:
    """Interview Answer Service Tests"""

    def test_submit_answer(self, db_session, test_user, test_job):
        """Test submitting interview answer"""
        session = InterviewSessionService.create_session(
            db=db_session,
            user_id=test_user.id,
            job_id=test_job.id,
            session_type="technical",
            total_questions=1,
        )

        questions = InterviewQuestionService.generate_questions(
            db=db_session,
            session_id=session.id,
            session_type="technical",
            num_questions=1,
        )

        answer = InterviewAnswerService.submit_answer(
            db=db_session,
            question_id=questions[0].id,
            user_answer="I would use a binary search algorithm",
            answer_time_seconds=120,
        )

        assert answer is not None
        assert answer.question_id == questions[0].id
        assert answer.user_answer == "I would use a binary search algorithm"
        assert answer.answer_time_seconds == 120

    def test_evaluate_answer(self, db_session, test_user, test_job):
        """Test evaluating answer with AI"""
        session = InterviewSessionService.create_session(
            db=db_session,
            user_id=test_user.id,
            job_id=test_job.id,
            session_type="technical",
            total_questions=1,
        )

        questions = InterviewQuestionService.generate_questions(
            db=db_session,
            session_id=session.id,
            session_type="technical",
            num_questions=1,
        )

        answer = InterviewAnswerService.submit_answer(
            db=db_session,
            question_id=questions[0].id,
            user_answer="This is my answer",
            answer_time_seconds=90,
        )

        evaluated = InterviewAnswerService.evaluate_answer(
            db_session, answer.id, questions[0].question_text
        )

        assert evaluated.score is not None
        assert 0 <= evaluated.score <= 100
        assert evaluated.feedback is not None

    def test_get_session_answers(self, db_session, test_user, test_job):
        """Test retrieving session answers"""
        session = InterviewSessionService.create_session(
            db=db_session,
            user_id=test_user.id,
            job_id=test_job.id,
            session_type="behavioral",
            total_questions=2,
        )

        questions = InterviewQuestionService.generate_questions(
            db=db_session,
            session_id=session.id,
            session_type="behavioral",
            num_questions=2,
        )

        for q in questions:
            InterviewAnswerService.submit_answer(
                db=db_session,
                question_id=q.id,
                user_answer="My answer",
                answer_time_seconds=60,
            )

        answers = InterviewAnswerService.get_session_answers(db_session, session.id)

        assert len(answers) == 2
        assert all(a.question_id in [q.id for q in questions] for a in answers)


class TestInterviewMetricsService:
    """Interview Metrics Service Tests"""

    def test_get_or_create_metrics(self, db_session, test_user):
        """Test creating metrics for new user"""
        metrics = InterviewMetricsService.get_or_create_metrics(
            db_session, test_user.id
        )

        assert metrics is not None
        assert metrics.user_id == test_user.id
        assert metrics.total_sessions == 0
        assert metrics.total_questions == 0

    def test_get_metrics(self, db_session, test_user):
        """Test retrieving metrics"""
        InterviewMetricsService.get_or_create_metrics(db_session, test_user.id)

        metrics = InterviewMetricsService.get_metrics(db_session, test_user.id)

        assert metrics is not None
        assert metrics.user_id == test_user.id

    def test_update_metrics(self, db_session, test_user, test_job):
        """Test updating metrics after session"""
        # Create session with answers
        session = InterviewSessionService.create_session(
            db=db_session,
            user_id=test_user.id,
            job_id=test_job.id,
            session_type="technical",
            total_questions=2,
        )

        questions = InterviewQuestionService.generate_questions(
            db=db_session,
            session_id=session.id,
            session_type="technical",
            num_questions=2,
        )

        for q in questions:
            answer = InterviewAnswerService.submit_answer(
                db=db_session,
                question_id=q.id,
                user_answer="Answer",
            )
            InterviewAnswerService.evaluate_answer(db_session, answer.id, q.question_text)

        InterviewSessionService.complete_session(db_session, session.id, 80)
        InterviewMetricsService.update_metrics(db_session, test_user.id)

        metrics = InterviewMetricsService.get_metrics(db_session, test_user.id)

        assert metrics.total_sessions >= 1
        assert metrics.total_questions >= 2


class TestInterviewAPI:
    """Interview API Endpoint Tests"""

    def test_create_session_endpoint(self, client, test_user, test_job, auth_headers):
        """Test POST /api/interviews"""
        response = client.post(
            "/api/interviews",
            json={
                "job_id": str(test_job.id),
                "session_type": "technical",
                "difficulty_level": "medium",
                "industry": "tech",
                "role": "backend",
                "num_questions": 5,
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["session_type"] == "technical"
        assert data["difficulty_level"] == "medium"

    def test_get_session_endpoint(self, client, test_user, test_job, auth_headers, db_session):
        """Test GET /api/interviews/{session_id}"""
        session = InterviewSessionService.create_session(
            db=db_session,
            user_id=test_user.id,
            job_id=test_job.id,
            session_type="behavioral",
            total_questions=3,
        )

        response = client.get(
            f"/api/interviews/{session.id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(session.id)

    def test_list_sessions_endpoint(self, client, test_user, test_job, auth_headers, db_session):
        """Test GET /api/interviews"""
        for _ in range(3):
            InterviewSessionService.create_session(
                db=db_session,
                user_id=test_user.id,
                job_id=test_job.id,
                session_type="general",
                total_questions=2,
            )

        response = client.get(
            "/api/interviews",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    def test_get_questions_endpoint(self, client, test_user, test_job, auth_headers, db_session):
        """Test GET /api/interviews/{session_id}/questions"""
        session = InterviewSessionService.create_session(
            db=db_session,
            user_id=test_user.id,
            job_id=test_job.id,
            session_type="technical",
            total_questions=2,
        )

        InterviewQuestionService.generate_questions(
            db=db_session,
            session_id=session.id,
            session_type="technical",
            num_questions=2,
        )

        response = client.get(
            f"/api/interviews/{session.id}/questions",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_submit_answer_endpoint(self, client, test_user, test_job, auth_headers, db_session):
        """Test POST /api/interviews/{question_id}/answer"""
        session = InterviewSessionService.create_session(
            db=db_session,
            user_id=test_user.id,
            job_id=test_job.id,
            session_type="behavioral",
            total_questions=1,
        )

        questions = InterviewQuestionService.generate_questions(
            db=db_session,
            session_id=session.id,
            session_type="behavioral",
            num_questions=1,
        )

        response = client.post(
            f"/api/interviews/{questions[0].id}/answer",
            json={
                "user_answer": "I would handle this by...",
                "answer_time_seconds": 120,
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["user_answer"] == "I would handle this by..."

    def test_complete_session_endpoint(self, client, test_user, test_job, auth_headers, db_session):
        """Test POST /api/interviews/{session_id}/complete"""
        session = InterviewSessionService.create_session(
            db=db_session,
            user_id=test_user.id,
            job_id=test_job.id,
            session_type="general",
            total_questions=2,
        )

        questions = InterviewQuestionService.generate_questions(
            db=db_session,
            session_id=session.id,
            session_type="general",
            num_questions=2,
        )

        for q in questions:
            answer = InterviewAnswerService.submit_answer(
                db=db_session,
                question_id=q.id,
                user_answer="Answer",
            )
            InterviewAnswerService.evaluate_answer(db_session, answer.id, q.question_text)

        response = client.post(
            f"/api/interviews/{session.id}/complete",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["overall_score"] >= 0
        assert data["questions_answered"] == 2

    def test_get_metrics_endpoint(self, client, test_user, auth_headers, db_session):
        """Test GET /api/interviews/metrics/performance"""
        InterviewMetricsService.get_or_create_metrics(db_session, test_user.id)

        response = client.get(
            "/api/interviews/metrics/performance",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == str(test_user.id)
        assert data["total_sessions"] == 0
