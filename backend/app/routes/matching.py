"""
Job matching API routes
"""

import logging
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.matching import (
    JobMatchResponse,
    JobMatchDetailResponse,
    MatchingResponse,
    SkillAnalysis,
    BulkMatchingResponse,
    UserMatchesList,
)
from app.services.matching_service import (
    EmbeddingService,
    SkillAnalysisService,
    MatchingService,
)
from app.services.job_service import JobService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/matching", tags=["matching"])


# Embedding endpoints
@router.post("/embeddings/resume", response_model=dict)
def create_resume_embedding(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create or update resume embedding"""
    try:
        embedding = EmbeddingService.create_resume_embedding(db, current_user.id)
        return {
            "user_id": str(embedding.user_id),
            "created_at": embedding.created_at,
            "skills_extracted": embedding.skills_extracted,
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/embeddings/job/{job_id}", response_model=dict)
def create_job_embedding(
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create or update job embedding"""
    try:
        embedding = EmbeddingService.create_job_embedding(db, job_id)
        return {
            "job_id": str(embedding.job_id),
            "created_at": embedding.created_at,
            "skills": embedding.skills_required_normalized,
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# Skill analysis endpoints
@router.get("/skills/analysis/{job_id}", response_model=SkillAnalysis)
def analyze_skills(
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Analyze skill match with job"""
    try:
        analysis = SkillAnalysisService.analyze_skills(db, current_user.id, job_id)
        return analysis
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# Job matching endpoints
@router.post("/jobs/{job_id}", response_model=JobMatchResponse)
def compute_job_match(
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Compute match score for a specific job"""
    try:
        match = MatchingService.compute_match(db, current_user.id, job_id)
        return match
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/jobs/{job_id}/detail", response_model=JobMatchDetailResponse)
def get_match_detail(
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get detailed match information"""
    try:
        match = MatchingService.get_match(db, current_user.id, job_id)
        if not match:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Match not found"
            )

        job = JobService.get_job(db, job_id)
        return {
            **match.__dict__,
            "job": job.__dict__ if job else None,
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/top", response_model=UserMatchesList)
def get_top_matches(
    min_percentage: int = Query(0, ge=0, le=100),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get top job matches for user"""
    try:
        total, matches = MatchingService.get_user_matches(
            db, current_user.id, min_percentage, skip, limit
        )
        return UserMatchesList(
            total=total,
            skip=skip,
            limit=limit,
            matches=matches,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/high", response_model=UserMatchesList)
def get_high_matches(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get high match jobs (>75%)"""
    try:
        total, matches = MatchingService.get_user_matches(
            db, current_user.id, min_percentage=75, skip=skip, limit=limit
        )
        return UserMatchesList(
            total=total,
            skip=skip,
            limit=limit,
            matches=matches,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/moderate", response_model=UserMatchesList)
def get_moderate_matches(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get moderate match jobs (50-75%)"""
    try:
        total, matches = MatchingService.get_user_matches(
            db, current_user.id, min_percentage=50, skip=skip, limit=limit
        )
        # Filter to only those < 75%
        matches = [m for m in matches if m.match_percentage < 75]
        return UserMatchesList(
            total=len(matches),
            skip=skip,
            limit=limit,
            matches=matches,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/bulk", response_model=BulkMatchingResponse)
def compute_bulk_matches(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Compute matches for all active jobs"""
    try:
        stats = MatchingService.compute_bulk_matches(db, current_user.id)
        return BulkMatchingResponse(
            total_matches=stats["total_matches"],
            matched_jobs=stats["matched_jobs"],
            high_matches=stats["high_matches"],
            moderate_matches=stats["moderate_matches"],
            low_matches=stats["low_matches"],
            timestamp=datetime.now(timezone.utc),
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# Import after definition to avoid circular imports
from datetime import datetime, timezone
