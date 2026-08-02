"""
Tests for browser automation
"""

import pytest
import uuid

from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from app.main import app
from app.models.automation import AutomationJob, AutomationStep
from app.models.user import User
from app.models.job import Job
from app.services.automation_service import AutomationService

client = TestClient(app)


@pytest.fixture
def sample_job(db: Session, sample_user: User) -> Job:
    """Create a sample job"""
    job = Job(
        id=uuid.uuid4(),
        user_id=sample_user.id,
        title="Engineer",
        company="Tech Corp",
        location="SF",
        description="Job",
        job_type="Full-time",
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


class TestAutomationService:
    """Test automation service"""

    def test_create_automation_job(self, db: Session, sample_user: User, sample_job: Job):
        """Test creating automation job"""
        job = AutomationService.create_automation_job(
            db=db,
            user_id=sample_user.id,
            job_id=sample_job.id,
            job_url="https://example.com/job/123",
            automation_type="linkedin_apply",
        )

        assert job.id is not None
        assert job.user_id == sample_user.id
        assert job.status == "pending"

    def test_get_automation_job(self, db: Session, sample_user: User, sample_job: Job):
        """Test retrieving automation job"""
        created = AutomationService.create_automation_job(
            db, sample_user.id, sample_job.id, "https://example.com/job/123"
        )

        retrieved = AutomationService.get_automation_job(db, created.id)

        assert retrieved is not None
        assert retrieved.id == created.id

    def test_update_automation_status(
        self, db: Session, sample_user: User, sample_job: Job
    ):
        """Test updating automation status"""
        job = AutomationService.create_automation_job(
            db, sample_user.id, sample_job.id, "https://example.com/job/123"
        )

        updated = AutomationService.update_automation_job_status(
            db, job.id, "in_progress"
        )

        assert updated.status == "in_progress"
        assert updated.started_at is not None

    def test_add_automation_step(self, db: Session, sample_user: User, sample_job: Job):
        """Test adding automation step"""
        job = AutomationService.create_automation_job(
            db, sample_user.id, sample_job.id, "https://example.com/job/123"
        )

        step = AutomationService.add_automation_step(
            db=db,
            automation_id=job.id,
            step_order=1,
            action_type="click",
            selector="#apply-button",
            step_name="Click apply button",
        )

        assert step.id is not None
        assert step.automation_job_id == job.id
        assert step.action_type == "click"

    def test_get_automation_steps(self, db: Session, sample_user: User, sample_job: Job):
        """Test retrieving automation steps"""
        job = AutomationService.create_automation_job(
            db, sample_user.id, sample_job.id, "https://example.com/job/123"
        )

        AutomationService.add_automation_step(
            db, job.id, 1, "click", step_name="Step 1"
        )
        AutomationService.add_automation_step(
            db, job.id, 2, "type", step_name="Step 2"
        )

        steps = AutomationService.get_automation_steps(db, job.id)

        assert len(steps) == 2
        assert steps[0].step_order == 1

    def test_add_automation_log(self, db: Session, sample_user: User, sample_job: Job):
        """Test adding automation log"""
        job = AutomationService.create_automation_job(
            db, sample_user.id, sample_job.id, "https://example.com/job/123"
        )

        log = AutomationService.add_automation_log(
            db, job.id, "INFO", "Automation started"
        )

        assert log.id is not None
        assert log.automation_job_id == job.id
        assert log.log_level == "INFO"

    def test_get_automation_logs(self, db: Session, sample_user: User, sample_job: Job):
        """Test retrieving logs"""
        job = AutomationService.create_automation_job(
            db, sample_user.id, sample_job.id, "https://example.com/job/123"
        )

        AutomationService.add_automation_log(db, job.id, "INFO", "Started")
        AutomationService.add_automation_log(db, job.id, "INFO", "Processing")

        logs = AutomationService.get_automation_logs(db, job.id)

        assert len(logs) >= 2

    def test_increment_retry(self, db: Session, sample_user: User, sample_job: Job):
        """Test incrementing retry count"""
        job = AutomationService.create_automation_job(
            db, sample_user.id, sample_job.id, "https://example.com/job/123"
        )

        initial_retry = job.current_retry

        updated = AutomationService.increment_retry(db, job.id)

        assert updated.current_retry == initial_retry + 1

    def test_delete_automation_job(self, db: Session, sample_user: User, sample_job: Job):
        """Test deleting automation job"""
        job = AutomationService.create_automation_job(
            db, sample_user.id, sample_job.id, "https://example.com/job/123"
        )

        AutomationService.delete_automation_job(db, job.id)

        retrieved = AutomationService.get_automation_job(db, job.id)
        assert retrieved is None


class TestAutomationAPI:
    """Test automation API"""

    def test_create_automation_api(
        self,
        db: Session,
        sample_user: User,
        sample_job: Job,
        auth_token: str,
    ):
        """Test creating automation via API"""
        response = client.post(
            "/api/automation",
            json={
                "job_id": str(sample_job.id),
                "job_url": "https://example.com/job/123",
                "automation_type": "linkedin_apply",
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "pending"

    def test_list_automation_api(
        self,
        db: Session,
        sample_user: User,
        sample_job: Job,
        auth_token: str,
    ):
        """Test listing automation jobs via API"""
        AutomationService.create_automation_job(
            db, sample_user.id, sample_job.id, "https://example.com/job/123"
        )

        response = client.get(
            "/api/automation",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_automation_status_api(
        self,
        db: Session,
        sample_user: User,
        sample_job: Job,
        auth_token: str,
    ):
        """Test getting automation status via API"""
        job = AutomationService.create_automation_job(
            db, sample_user.id, sample_job.id, "https://example.com/job/123"
        )

        response = client.get(
            f"/api/automation/{job.id}/status",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "pending"

    def test_add_automation_step_api(
        self,
        db: Session,
        sample_user: User,
        sample_job: Job,
        auth_token: str,
    ):
        """Test adding step via API"""
        job = AutomationService.create_automation_job(
            db, sample_user.id, sample_job.id, "https://example.com/job/123"
        )

        response = client.post(
            f"/api/automation/{job.id}/steps",
            json={
                "step_order": 1,
                "action_type": "click",
                "selector": "#apply",
                "step_name": "Click apply",
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["action_type"] == "click"

    def test_start_stop_automation_api(
        self,
        db: Session,
        sample_user: User,
        sample_job: Job,
        auth_token: str,
    ):
        """Test start/stop automation via API"""
        job = AutomationService.create_automation_job(
            db, sample_user.id, sample_job.id, "https://example.com/job/123"
        )

        # Start
        start_response = client.post(
            f"/api/automation/{job.id}/start",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert start_response.status_code == 200
        assert start_response.json()["status"] == "in_progress"

        # Stop
        stop_response = client.post(
            f"/api/automation/{job.id}/stop",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert stop_response.status_code == 200
        assert stop_response.json()["status"] == "paused"
