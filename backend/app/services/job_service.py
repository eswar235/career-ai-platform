"""
Job search service for handling job listings, search, filtering, and saved jobs
"""

import logging
import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from app.models.job import Job, SavedJob, JobSearchHistory, JobApplication
from app.schemas.job import (
    JobCreate,
    JobUpdate,
    JobSearchFilters,
    SavedJobCreate,
    JobApplicationCreate,
    JobApplicationUpdate,
)

logger = logging.getLogger(__name__)


class JobService:
    """Service for managing job postings"""

    @staticmethod
    def create_job(db: Session, data: JobCreate) -> Job:
        """Create a new job posting"""
        job = Job(
            title=data.title,
            company_name=data.company_name,
            company_id=data.company_id,
            location=data.location,
            job_type=data.job_type,
            salary_min=data.salary_min,
            salary_max=data.salary_max,
            salary_currency=data.salary_currency or "USD",
            description=data.description,
            requirements=data.requirements,
            benefits=data.benefits,
            industry=data.industry,
            experience_level=data.experience_level,
            skills_required=data.skills_required,
            posted_date=data.posted_date,
            application_deadline=data.application_deadline,
            source=data.source,
            source_url=data.source_url,
        )

        db.add(job)
        db.commit()
        db.refresh(job)

        logger.info(f"Job created: {job.id} - {data.title} at {data.company_name}")
        return job

    @staticmethod
    def get_job(db: Session, job_id: uuid.UUID) -> Job | None:
        """Get job by ID"""
        return db.query(Job).filter(Job.id == job_id).first()

    @staticmethod
    def search_jobs(db: Session, filters: JobSearchFilters) -> tuple[int, list[Job]]:
        """Search jobs with filters"""
        query = db.query(Job).filter(Job.is_active == True)

        # Keyword search in title, description, requirements
        if filters.keyword:
            search_term = f"%{filters.keyword}%"
            query = query.filter(
                or_(
                    Job.title.ilike(search_term),
                    Job.description.ilike(search_term),
                    Job.requirements.ilike(search_term),
                )
            )

        # Location filter
        if filters.location:
            query = query.filter(Job.location.ilike(f"%{filters.location}%"))

        # Job type filter
        if filters.job_type:
            query = query.filter(Job.job_type.ilike(filters.job_type))

        # Experience level filter
        if filters.experience_level:
            query = query.filter(Job.experience_level.ilike(filters.experience_level))

        # Salary range filter
        if filters.salary_min is not None:
            query = query.filter(
                or_(Job.salary_max.is_(None), Job.salary_max >= filters.salary_min)
            )
        if filters.salary_max is not None:
            query = query.filter(
                or_(Job.salary_min.is_(None), Job.salary_min <= filters.salary_max)
            )

        # Industry filter
        if filters.industry:
            query = query.filter(Job.industry.ilike(filters.industry))

        # Company filter
        if filters.company_name:
            query = query.filter(Job.company_name.ilike(f"%{filters.company_name}%"))

        # Posted date filter
        if filters.posted_after:
            query = query.filter(Job.posted_date >= filters.posted_after)

        # Get total count
        total = query.count()

        # Sorting
        if filters.sort_by == "salary":
            query = query.order_by(desc(Job.salary_max))
        else:
            query = query.order_by(desc(Job.posted_date))

        # Pagination
        query = query.offset(filters.skip).limit(filters.limit)

        jobs = query.all()
        logger.info(f"Job search executed: keyword={filters.keyword}, total={total}")

        return total, jobs

    @staticmethod
    def update_job(db: Session, job_id: uuid.UUID, data: JobUpdate) -> Job:
        """Update job posting"""
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise ValueError("Job not found")

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(job, field, value)

        job.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(job)

        logger.info(f"Job {job_id} updated")
        return job

    @staticmethod
    def deactivate_job(db: Session, job_id: uuid.UUID) -> Job:
        """Deactivate (soft delete) a job"""
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise ValueError("Job not found")

        job.is_active = False
        job.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(job)

        logger.info(f"Job {job_id} deactivated")
        return job


class SavedJobService:
    """Service for managing saved jobs"""

    @staticmethod
    def save_job(db: Session, user_id: uuid.UUID, data: SavedJobCreate) -> SavedJob:
        """Save a job"""
        # Check if already saved
        existing = (
            db.query(SavedJob)
            .filter(and_(SavedJob.user_id == user_id, SavedJob.job_id == data.job_id))
            .first()
        )
        if existing:
            raise ValueError("Job already saved")

        # Verify job exists
        job = db.query(Job).filter(Job.id == data.job_id).first()
        if not job:
            raise ValueError("Job not found")

        saved_job = SavedJob(
            user_id=user_id,
            job_id=data.job_id,
            notes=data.notes,
        )

        db.add(saved_job)
        db.commit()
        db.refresh(saved_job)

        logger.info(f"Job {data.job_id} saved by user {user_id}")
        return saved_job

    @staticmethod
    def get_saved_jobs(db: Session, user_id: uuid.UUID, skip: int = 0, limit: int = 20) -> tuple[int, list[SavedJob]]:
        """Get user's saved jobs"""
        query = db.query(SavedJob).filter(SavedJob.user_id == user_id)
        total = query.count()

        saved_jobs = query.order_by(desc(SavedJob.saved_at)).offset(skip).limit(limit).all()
        return total, saved_jobs

    @staticmethod
    def unsave_job(db: Session, user_id: uuid.UUID, job_id: uuid.UUID) -> bool:
        """Remove a saved job"""
        saved_job = (
            db.query(SavedJob)
            .filter(and_(SavedJob.user_id == user_id, SavedJob.job_id == job_id))
            .first()
        )
        if not saved_job:
            raise ValueError("Saved job not found")

        db.delete(saved_job)
        db.commit()

        logger.info(f"Job {job_id} unsaved by user {user_id}")
        return True

    @staticmethod
    def is_job_saved(db: Session, user_id: uuid.UUID, job_id: uuid.UUID) -> bool:
        """Check if job is saved"""
        return (
            db.query(SavedJob)
            .filter(and_(SavedJob.user_id == user_id, SavedJob.job_id == job_id))
            .first()
            is not None
        )


class JobSearchHistoryService:
    """Service for tracking job search history"""

    @staticmethod
    def record_search(
        db: Session,
        user_id: uuid.UUID,
        search_query: str | None,
        filters: dict | None,
        results_count: int,
    ) -> JobSearchHistory:
        """Record a search in history"""
        history = JobSearchHistory(
            user_id=user_id,
            search_query=search_query,
            filters_applied=filters,
            results_count=results_count,
        )

        db.add(history)
        db.commit()
        db.refresh(history)

        logger.info(f"Search recorded for user {user_id}: {search_query}")
        return history

    @staticmethod
    def get_search_history(
        db: Session, user_id: uuid.UUID, limit: int = 20
    ) -> list[JobSearchHistory]:
        """Get user's search history"""
        return (
            db.query(JobSearchHistory)
            .filter(JobSearchHistory.user_id == user_id)
            .order_by(desc(JobSearchHistory.searched_at))
            .limit(limit)
            .all()
        )


class JobApplicationService:
    """Service for managing job applications"""

    @staticmethod
    def apply_for_job(
        db: Session, user_id: uuid.UUID, data: JobApplicationCreate
    ) -> JobApplication:
        """Record a job application"""
        # Check if already applied
        existing = (
            db.query(JobApplication)
            .filter(
                and_(
                    JobApplication.user_id == user_id,
                    JobApplication.job_id == data.job_id,
                )
            )
            .first()
        )
        if existing:
            raise ValueError("Already applied to this job")

        # Verify job exists
        job = db.query(Job).filter(Job.id == data.job_id).first()
        if not job:
            raise ValueError("Job not found")

        application = JobApplication(
            user_id=user_id,
            job_id=data.job_id,
            status="applied",
            notes=data.notes,
        )

        db.add(application)
        db.commit()
        db.refresh(application)

        logger.info(f"Application created: user={user_id}, job={data.job_id}")
        return application

    @staticmethod
    def get_applications(
        db: Session, user_id: uuid.UUID, skip: int = 0, limit: int = 20
    ) -> tuple[int, list[JobApplication]]:
        """Get user's job applications"""
        query = db.query(JobApplication).filter(JobApplication.user_id == user_id)
        total = query.count()

        applications = (
            query.order_by(desc(JobApplication.applied_date))
            .offset(skip)
            .limit(limit)
            .all()
        )
        return total, applications

    @staticmethod
    def get_application_by_status(
        db: Session, user_id: uuid.UUID, status: str, skip: int = 0, limit: int = 20
    ) -> tuple[int, list[JobApplication]]:
        """Get applications by status"""
        query = db.query(JobApplication).filter(
            and_(JobApplication.user_id == user_id, JobApplication.status == status)
        )
        total = query.count()

        applications = (
            query.order_by(desc(JobApplication.applied_date))
            .offset(skip)
            .limit(limit)
            .all()
        )
        return total, applications

    @staticmethod
    def update_application(
        db: Session,
        application_id: uuid.UUID,
        user_id: uuid.UUID,
        data: JobApplicationUpdate,
    ) -> JobApplication:
        """Update application status"""
        application = (
            db.query(JobApplication)
            .filter(
                and_(
                    JobApplication.id == application_id,
                    JobApplication.user_id == user_id,
                )
            )
            .first()
        )
        if not application:
            raise ValueError("Application not found")

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(application, field, value)

        application.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(application)

        logger.info(f"Application {application_id} updated to status {data.status}")
        return application

    @staticmethod
    def get_application_stats(db: Session, user_id: uuid.UUID) -> dict:
        """Get application statistics for user"""
        query = db.query(JobApplication).filter(JobApplication.user_id == user_id)

        total_applications = query.count()
        applied_count = query.filter(JobApplication.status == "applied").count()
        interviewed_count = query.filter(JobApplication.status == "interviewed").count()
        offered_count = query.filter(JobApplication.status == "offered").count()
        rejected_count = query.filter(JobApplication.status == "rejected").count()

        return {
            "total": total_applications,
            "applied": applied_count,
            "interviewed": interviewed_count,
            "offered": offered_count,
            "rejected": rejected_count,
        }
