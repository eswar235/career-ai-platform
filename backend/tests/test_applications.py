"""
Tests for job application tracker
"""

import pytest
import uuid
from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from app.main import app
from app.models.application import JobApplication, Interview, JobOffer
from app.models.user import User
from app.models.job import Job
from app.services.application_service import ApplicationService
from app.services.interview_service import InterviewService
from app.services.offer_service import OfferService

client = TestClient(app)


@pytest.fixture
def sample_job(db: Session, sample_user: User) -> Job:
    """Create a sample job"""
    job = Job(
        id=uuid.uuid4(),
        user_id=sample_user.id,
        title="Senior Engineer",
        company="Tech Corp",
        location="SF",
        description="Job description",
        job_type="Full-time",
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


class TestApplicationService:
    """Test application service"""

    def test_create_application(self, db: Session, sample_user: User, sample_job: Job):
        """Test creating an application"""
        app = ApplicationService.create_application(
            db=db,
            user_id=sample_user.id,
            job_id=sample_job.id,
            applied_via="direct",
        )

        assert app.id is not None
        assert app.user_id == sample_user.id
        assert app.job_id == sample_job.id
        assert app.status == "applied"

    def test_get_application(self, db: Session, sample_user: User, sample_job: Job):
        """Test retrieving an application"""
        created = ApplicationService.create_application(
            db, sample_user.id, sample_job.id
        )

        retrieved = ApplicationService.get_application(db, created.id)

        assert retrieved is not None
        assert retrieved.id == created.id

    def test_update_application_status(
        self, db: Session, sample_user: User, sample_job: Job
    ):
        """Test updating application status"""
        app = ApplicationService.create_application(
            db, sample_user.id, sample_job.id
        )

        updated = ApplicationService.update_application_status(
            db, app.id, "interview_scheduled", "Interview scheduled for Tuesday"
        )

        assert updated.status == "interview_scheduled"
        assert "Interview scheduled" in updated.notes

    def test_get_user_applications(
        self, db: Session, sample_user: User, sample_job: Job
    ):
        """Test listing user applications"""
        ApplicationService.create_application(db, sample_user.id, sample_job.id)

        total, apps = ApplicationService.get_user_applications(db, sample_user.id)

        assert total >= 1
        assert len(apps) >= 1

    def test_delete_application(self, db: Session, sample_user: User, sample_job: Job):
        """Test deleting an application"""
        app = ApplicationService.create_application(
            db, sample_user.id, sample_job.id
        )

        ApplicationService.delete_application(db, app.id)

        retrieved = ApplicationService.get_application(db, app.id)
        assert retrieved is None


class TestInterviewService:
    """Test interview service"""

    def test_create_interview(self, db: Session, sample_user: User, sample_job: Job):
        """Test creating an interview"""
        app = ApplicationService.create_application(
            db, sample_user.id, sample_job.id
        )

        interview = InterviewService.create_interview(
            db=db,
            application_id=app.id,
            interview_type="phone",
            duration_minutes=30,
            interviewer_name="John Doe",
        )

        assert interview.id is not None
        assert interview.application_id == app.id
        assert interview.interview_type == "phone"

    def test_get_application_interviews(
        self, db: Session, sample_user: User, sample_job: Job
    ):
        """Test retrieving interviews"""
        app = ApplicationService.create_application(
            db, sample_user.id, sample_job.id
        )

        InterviewService.create_interview(
            db, app.id, interview_type="phone"
        )
        InterviewService.create_interview(
            db, app.id, interview_type="video"
        )

        interviews = InterviewService.get_application_interviews(db, app.id)

        assert len(interviews) >= 2

    def test_update_interview(self, db: Session, sample_user: User, sample_job: Job):
        """Test updating an interview"""
        app = ApplicationService.create_application(
            db, sample_user.id, sample_job.id
        )

        interview = InterviewService.create_interview(
            db, app.id, interview_type="phone"
        )

        updated = InterviewService.update_interview(
            db,
            interview.id,
            status="completed",
            feedback="Very good candidate",
            interview_score=8,
        )

        assert updated.status == "completed"
        assert updated.interview_score == 8

    def test_delete_interview(self, db: Session, sample_user: User, sample_job: Job):
        """Test deleting an interview"""
        app = ApplicationService.create_application(
            db, sample_user.id, sample_job.id
        )

        interview = InterviewService.create_interview(
            db, app.id, interview_type="phone"
        )

        InterviewService.delete_interview(db, interview.id)

        retrieved = InterviewService.get_interview(db, interview.id)
        assert retrieved is None


class TestOfferService:
    """Test offer service"""

    def test_create_offer(self, db: Session, sample_user: User, sample_job: Job):
        """Test creating an offer"""
        app = ApplicationService.create_application(
            db, sample_user.id, sample_job.id
        )

        offer = OfferService.create_offer(
            db=db,
            application_id=app.id,
            salary=150000,
            bonus=20000,
        )

        assert offer.id is not None
        assert offer.application_id == app.id
        assert offer.salary == 150000

    def test_accept_offer(self, db: Session, sample_user: User, sample_job: Job):
        """Test accepting an offer"""
        app = ApplicationService.create_application(
            db, sample_user.id, sample_job.id
        )

        offer = OfferService.create_offer(
            db, app.id, salary=150000
        )

        accepted = OfferService.accept_offer(db, offer.id)

        assert accepted.status == "accepted"
        assert accepted.accepted_date is not None

    def test_decline_offer(self, db: Session, sample_user: User, sample_job: Job):
        """Test declining an offer"""
        app = ApplicationService.create_application(
            db, sample_user.id, sample_job.id
        )

        offer = OfferService.create_offer(
            db, app.id, salary=150000
        )

        declined = OfferService.decline_offer(
            db, offer.id, reason="Found better opportunity"
        )

        assert declined.status == "declined"
        assert "Found better opportunity" in declined.negotiation_notes

    def test_delete_offer(self, db: Session, sample_user: User, sample_job: Job):
        """Test deleting an offer"""
        app = ApplicationService.create_application(
            db, sample_user.id, sample_job.id
        )

        offer = OfferService.create_offer(
            db, app.id, salary=150000
        )

        OfferService.delete_offer(db, offer.id)

        retrieved = OfferService.get_offer(db, offer.id)
        assert retrieved is None


class TestApplicationAPI:
    """Test application API endpoints"""

    def test_create_application_api(
        self,
        db: Session,
        sample_user: User,
        sample_job: Job,
        auth_token: str,
    ):
        """Test creating application via API"""
        response = client.post(
            "/api/applications",
            json={
                "job_id": str(sample_job.id),
                "applied_via": "direct",
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "applied"

    def test_list_applications_api(
        self,
        db: Session,
        sample_user: User,
        sample_job: Job,
        auth_token: str,
    ):
        """Test listing applications via API"""
        ApplicationService.create_application(
            db, sample_user.id, sample_job.id
        )

        response = client.get(
            "/api/applications",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_update_status_api(
        self,
        db: Session,
        sample_user: User,
        sample_job: Job,
        auth_token: str,
    ):
        """Test updating status via API"""
        app = ApplicationService.create_application(
            db, sample_user.id, sample_job.id
        )

        response = client.put(
            f"/api/applications/{app.id}/status?new_status=interview_scheduled",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "interview_scheduled"

    def test_interview_crud_api(
        self,
        db: Session,
        sample_user: User,
        sample_job: Job,
        auth_token: str,
    ):
        """Test interview CRUD via API"""
        app = ApplicationService.create_application(
            db, sample_user.id, sample_job.id
        )

        # Create
        create_response = client.post(
            f"/api/applications/{app.id}/interviews",
            json={
                "interview_type": "phone",
                "duration_minutes": 30,
                "interviewer_name": "John",
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert create_response.status_code == 200
        interview_id = create_response.json()["id"]

        # List
        list_response = client.get(
            f"/api/applications/{app.id}/interviews",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert list_response.status_code == 200

    def test_offer_workflow_api(
        self,
        db: Session,
        sample_user: User,
        sample_job: Job,
        auth_token: str,
    ):
        """Test offer workflow via API"""
        app = ApplicationService.create_application(
            db, sample_user.id, sample_job.id
        )

        # Create offer
        create_response = client.post(
            f"/api/applications/{app.id}/offers",
            json={
                "salary": 150000,
                "bonus": 20000,
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert create_response.status_code == 200
        offer_id = create_response.json()["id"]

        # Get offer
        get_response = client.get(
            f"/api/applications/{app.id}/offers",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert get_response.status_code == 200

        # Accept offer
        accept_response = client.post(
            f"/api/applications/offers/{offer_id}/accept",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert accept_response.status_code == 200
        data = accept_response.json()
        assert data["status"] == "accepted"
