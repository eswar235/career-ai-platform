"""
Job search API routes
"""

import logging
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.job import (
    JobCreate,
    JobUpdate,
    JobResponse,
    JobSearchFilters,
    JobSearchResults,
    SavedJobCreate,
    SavedJobResponse,
    JobSearchHistoryResponse,
    JobApplicationCreate,
    JobApplicationUpdate,
    JobApplicationResponse,
)
from app.services.job_service import (
    JobService,
    SavedJobService,
    JobSearchHistoryService,
    JobApplicationService,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


# Job endpoints
@router.post("/", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(
    data: JobCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new job posting (admin only)"""
    # TODO: Add admin check here
    try:
        job = JobService.create_job(db, data)
        return job
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/search", response_model=JobSearchResults)
def search_jobs(
    keyword: str = Query(None),
    location: str = Query(None),
    job_type: str = Query(None),
    experience_level: str = Query(None),
    salary_min: int = Query(None),
    salary_max: int = Query(None),
    industry: str = Query(None),
    company_name: str = Query(None),
    sort_by: str = Query("posted_date"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Search jobs with filters"""
    filters = JobSearchFilters(
        keyword=keyword,
        location=location,
        job_type=job_type,
        experience_level=experience_level,
        salary_min=salary_min,
        salary_max=salary_max,
        industry=industry,
        company_name=company_name,
        sort_by=sort_by,
        skip=skip,
        limit=limit,
    )

    try:
        total, jobs = JobService.search_jobs(db, filters)

        # Record search in history
        filter_dict = {
            k: v
            for k, v in filters.model_dump().items()
            if v is not None and k not in ["skip", "limit"]
        }
        JobSearchHistoryService.record_search(
            db, current_user.id, keyword, filter_dict if filter_dict else None, total
        )

        return JobSearchResults(
            total=total,
            skip=skip,
            limit=limit,
            jobs=jobs,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{job_id}", response_model=JobResponse)
def get_job(
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get job by ID"""
    job = JobService.get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return job


@router.patch("/{job_id}", response_model=JobResponse)
def update_job(
    job_id: uuid.UUID,
    data: JobUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update job posting (admin only)"""
    try:
        job = JobService.update_job(db, job_id, data)
        return job
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# Saved jobs endpoints
@router.post("/saved", response_model=SavedJobResponse, status_code=status.HTTP_201_CREATED)
def save_job(
    data: SavedJobCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Save a job"""
    try:
        saved_job = SavedJobService.save_job(db, current_user.id, data)
        return saved_job
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/saved/list", response_model=list[SavedJobResponse])
def get_saved_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get user's saved jobs"""
    total, saved_jobs = SavedJobService.get_saved_jobs(db, current_user.id, skip, limit)
    return saved_jobs


@router.get("/{job_id}/saved", response_model=dict)
def is_job_saved(
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Check if job is saved by user"""
    is_saved = SavedJobService.is_job_saved(db, current_user.id, job_id)
    return {"job_id": str(job_id), "is_saved": is_saved}


@router.delete("/saved/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def unsave_job(
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Unsave a job"""
    try:
        SavedJobService.unsave_job(db, current_user.id, job_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# Search history endpoints
@router.get("/history/list", response_model=list[JobSearchHistoryResponse])
def get_search_history(
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get user's search history"""
    history = JobSearchHistoryService.get_search_history(db, current_user.id, limit)
    return history


# Job applications endpoints
@router.post("/applications", response_model=JobApplicationResponse, status_code=status.HTTP_201_CREATED)
def apply_for_job(
    data: JobApplicationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Apply for a job"""
    try:
        application = JobApplicationService.apply_for_job(db, current_user.id, data)
        return application
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/applications/list", response_model=list[JobApplicationResponse])
def get_applications(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status_filter: str = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get user's job applications"""
    if status_filter:
        total, applications = JobApplicationService.get_application_by_status(
            db, current_user.id, status_filter, skip, limit
        )
    else:
        total, applications = JobApplicationService.get_applications(
            db, current_user.id, skip, limit
        )
    return applications


@router.patch("/applications/{application_id}", response_model=JobApplicationResponse)
def update_application(
    application_id: uuid.UUID,
    data: JobApplicationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update job application status"""
    try:
        application = JobApplicationService.update_application(
            db, application_id, current_user.id, data
        )
        return application
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/applications/stats", response_model=dict)
def get_application_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get application statistics"""
    stats = JobApplicationService.get_application_stats(db, current_user.id)
    return stats
