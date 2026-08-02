"""
Tests for job search services
"""

import uuid
from datetime import date
import pytest
from sqlalchemy.orm import Session

from app.services.job_service import (
    JobService,
    SavedJobService,
    JobSearchHistoryService,
    JobApplicationService,
)
from app.schemas.job import (
    JobCreate,
    JobSearchFilters,
    SavedJobCreate,
    JobApplicationCreate,
)


class TestJobService:
    """Tests for JobService"""

    def test_create_job(self, db: Session):
        """Test creating a job"""
        job_data = JobCreate(
            title="Software Engineer",
            company_name="Tech Corp",
            location="New York, NY",
            job_type="full-time",
            salary_min=100000,
            salary_max=150000,
            description="We're hiring a software engineer",
            posted_date=date(2024, 12, 20),
        )
        job = JobService.create_job(db, job_data)
        assert job.title == "Software Engineer"
        assert job.company_name == "Tech Corp"
        assert job.is_active is True

    def test_get_job(self, db: Session):
        """Test getting a job"""
        job_data = JobCreate(
            title="Engineer",
            company_name="Corp",
            posted_date=date(2024, 12, 20),
        )
        created_job = JobService.create_job(db, job_data)
        job = JobService.get_job(db, created_job.id)
        assert job.id == created_job.id

    def test_search_jobs_keyword(self, db: Session):
        """Test searching jobs by keyword"""
        # Create jobs
        job1 = JobService.create_job(
            db,
            JobCreate(
                title="Python Developer",
                company_name="Tech Corp",
                description="Looking for a Python developer",
                posted_date=date(2024, 12, 20),
            ),
        )
        job2 = JobService.create_job(
            db,
            JobCreate(
                title="Sales Manager",
                company_name="Sales Corp",
                posted_date=date(2024, 12, 20),
            ),
        )

        # Search by keyword
        filters = JobSearchFilters(keyword="Python")
        total, jobs = JobService.search_jobs(db, filters)
        assert total == 1
        assert jobs[0].id == job1.id

    def test_search_jobs_filters(self, db: Session):
        """Test searching jobs with multiple filters"""
        JobService.create_job(
            db,
            JobCreate(
                title="Senior Engineer",
                company_name="Tech Corp",
                location="New York, NY",
                experience_level="senior",
                salary_min=100000,
                salary_max=200000,
                posted_date=date(2024, 12, 20),
            ),
        )

        filters = JobSearchFilters(
            location="New York",
            experience_level="senior",
            salary_min=80000,
            salary_max=250000,
        )
        total, jobs = JobService.search_jobs(db, filters)
        assert total == 1

    def test_update_job(self, db: Session):
        """Test updating a job"""
        job = JobService.create_job(
            db,
            JobCreate(
                title="Engineer",
                company_name="Corp",
                posted_date=date(2024, 12, 20),
            ),
        )

        from app.schemas.job import JobUpdate
        updated = JobService.update_job(
            db, job.id, JobUpdate(title="Senior Engineer")
        )
        assert updated.title == "Senior Engineer"

    def test_deactivate_job(self, db: Session):
        """Test deactivating a job"""
        job = JobService.create_job(
            db,
            JobCreate(
                title="Engineer",
                company_name="Corp",
                posted_date=date(2024, 12, 20),
            ),
        )

        deactivated = JobService.deactivate_job(db, job.id)
        assert deactivated.is_active is False


class TestSavedJobService:
    """Tests for SavedJobService"""

    def test_save_job(self, db: Session, test_user_id: uuid.UUID):
        """Test saving a job"""
        job = JobService.create_job(
            db,
            JobCreate(
                title="Engineer",
                company_name="Corp",
                posted_date=date(2024, 12, 20),
            ),
        )

        saved = SavedJobService.save_job(
            db, test_user_id, SavedJobCreate(job_id=job.id)
        )
        assert saved.job_id == job.id
        assert saved.user_id == test_user_id

    def test_duplicate_save(self, db: Session, test_user_id: uuid.UUID):
        """Test saving a job twice"""
        job = JobService.create_job(
            db,
            JobCreate(
                title="Engineer",
                company_name="Corp",
                posted_date=date(2024, 12, 20),
            ),
        )

        SavedJobService.save_job(db, test_user_id, SavedJobCreate(job_id=job.id))

        with pytest.raises(ValueError):
            SavedJobService.save_job(
                db, test_user_id, SavedJobCreate(job_id=job.id)
            )

    def test_get_saved_jobs(self, db: Session, test_user_id: uuid.UUID):
        """Test getting saved jobs"""
        job1 = JobService.create_job(
            db, JobCreate(title="Job 1", company_name="Corp", posted_date=date(2024, 12, 20))
        )
        job2 = JobService.create_job(
            db, JobCreate(title="Job 2", company_name="Corp", posted_date=date(2024, 12, 20))
        )

        SavedJobService.save_job(db, test_user_id, SavedJobCreate(job_id=job1.id))
        SavedJobService.save_job(db, test_user_id, SavedJobCreate(job_id=job2.id))

        total, saved_jobs = SavedJobService.get_saved_jobs(db, test_user_id)
        assert total == 2
        assert len(saved_jobs) == 2

    def test_is_job_saved(self, db: Session, test_user_id: uuid.UUID):
        """Test checking if job is saved"""
        job = JobService.create_job(
            db,
            JobCreate(
                title="Engineer",
                company_name="Corp",
                posted_date=date(2024, 12, 20),
            ),
        )

        is_saved = SavedJobService.is_job_saved(db, test_user_id, job.id)
        assert is_saved is False

        SavedJobService.save_job(db, test_user_id, SavedJobCreate(job_id=job.id))
        is_saved = SavedJobService.is_job_saved(db, test_user_id, job.id)
        assert is_saved is True


class TestJobApplicationService:
    """Tests for JobApplicationService"""

    def test_apply_for_job(self, db: Session, test_user_id: uuid.UUID):
        """Test applying for a job"""
        job = JobService.create_job(
            db,
            JobCreate(
                title="Engineer",
                company_name="Corp",
                posted_date=date(2024, 12, 20),
            ),
        )

        application = JobApplicationService.apply_for_job(
            db, test_user_id, JobApplicationCreate(job_id=job.id)
        )
        assert application.user_id == test_user_id
        assert application.job_id == job.id
        assert application.status == "applied"

    def test_duplicate_application(self, db: Session, test_user_id: uuid.UUID):
        """Test applying for same job twice"""
        job = JobService.create_job(
            db,
            JobCreate(
                title="Engineer",
                company_name="Corp",
                posted_date=date(2024, 12, 20),
            ),
        )

        JobApplicationService.apply_for_job(
            db, test_user_id, JobApplicationCreate(job_id=job.id)
        )

        with pytest.raises(ValueError):
            JobApplicationService.apply_for_job(
                db, test_user_id, JobApplicationCreate(job_id=job.id)
            )

    def test_get_applications(self, db: Session, test_user_id: uuid.UUID):
        """Test getting user applications"""
        job1 = JobService.create_job(
            db, JobCreate(title="Job 1", company_name="Corp", posted_date=date(2024, 12, 20))
        )
        job2 = JobService.create_job(
            db, JobCreate(title="Job 2", company_name="Corp", posted_date=date(2024, 12, 20))
        )

        JobApplicationService.apply_for_job(
            db, test_user_id, JobApplicationCreate(job_id=job1.id)
        )
        JobApplicationService.apply_for_job(
            db, test_user_id, JobApplicationCreate(job_id=job2.id)
        )

        total, applications = JobApplicationService.get_applications(db, test_user_id)
        assert total == 2

    def test_application_stats(self, db: Session, test_user_id: uuid.UUID):
        """Test getting application statistics"""
        job = JobService.create_job(
            db,
            JobCreate(
                title="Engineer",
                company_name="Corp",
                posted_date=date(2024, 12, 20),
            ),
        )

        app = JobApplicationService.apply_for_job(
            db, test_user_id, JobApplicationCreate(job_id=job.id)
        )

        from app.schemas.job import JobApplicationUpdate
        JobApplicationService.update_application(
            db, app.id, test_user_id, JobApplicationUpdate(status="interviewed")
        )

        stats = JobApplicationService.get_application_stats(db, test_user_id)
        assert stats["total"] == 1
        assert stats["interviewed"] == 1
