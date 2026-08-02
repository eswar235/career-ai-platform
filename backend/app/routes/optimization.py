"""
Resume optimization API routes
"""

import logging
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.optimization import (
    ResumeOptimizationCreate,
    ResumeOptimizationResponse,
    ResumeOptimizationDetailResponse,
    TailoredResumeCreate,
    TailoredResumeResponse,
    OptimizationScoreBreakdown,
    KeywordAnalysis,
)
from app.services.optimization_service import (
    OptimizationService,
    KeywordService,
)
from app.services.tailoring_service import TailoringService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/optimization", tags=["optimization"])


# Resume analysis endpoints
@router.post("/analyze", response_model=ResumeOptimizationResponse)
def analyze_resume(
    data: ResumeOptimizationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Analyze resume and generate optimization report"""
    try:
        optimization = OptimizationService.analyze_resume(
            db, current_user.id, data.original_content
        )
        return optimization
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/analysis", response_model=ResumeOptimizationDetailResponse)
def get_analysis(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get resume analysis"""
    try:
        optimization = OptimizationService.get_optimization(db, current_user.id)
        if not optimization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No analysis found"
            )
        return optimization
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/scores", response_model=OptimizationScoreBreakdown)
def get_scores(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get optimization score breakdown"""
    try:
        optimization = OptimizationService.get_optimization(db, current_user.id)
        if not optimization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No analysis found"
            )

        return OptimizationScoreBreakdown(
            ats_score=optimization.ats_score or 0,
            keyword_score=optimization.keyword_score or 0,
            formatting_score=optimization.formatting_score or 0,
            readability_score=optimization.readability_score or 0,
            overall_score=optimization.overall_score or 0,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# Optimization endpoints
@router.post("/optimize", response_model=dict)
def optimize_resume(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Generate optimized version of resume"""
    try:
        optimization = OptimizationService.get_optimization(db, current_user.id)
        if not optimization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No analysis found"
            )

        optimized = OptimizationService.optimize_resume(
            db, current_user.id, optimization.original_content
        )

        return {
            "optimized_content": optimized,
            "improved": True,
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/optimized", response_model=dict)
def get_optimized(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get optimized resume"""
    try:
        optimization = OptimizationService.get_optimization(db, current_user.id)
        if not optimization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No analysis found"
            )

        return {
            "original_content": optimization.original_content,
            "optimized_content": optimization.optimized_content,
            "overall_score": optimization.overall_score,
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# Keyword analysis endpoints
@router.get("/keywords", response_model=dict)
def analyze_keywords(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get keyword analysis"""
    try:
        optimization = OptimizationService.get_optimization(db, current_user.id)
        if not optimization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No analysis found"
            )

        keywords = KeywordService.extract_keywords(optimization.original_content)
        return {
            "keywords": keywords,
            "keyword_count": len(keywords),
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# Tailored resume endpoints
@router.post("/tailor/{job_id}", response_model=TailoredResumeResponse)
def create_tailored_resume(
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create job-specific tailored resume"""
    try:
        optimization = OptimizationService.get_optimization(db, current_user.id)
        if not optimization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No base resume found"
            )

        tailored = TailoringService.create_tailored_resume(
            db, current_user.id, job_id, optimization.original_content
        )
        return tailored
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/tailored/{job_id}", response_model=TailoredResumeResponse)
def get_tailored_resume(
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get tailored resume for job"""
    try:
        tailored = TailoringService.get_tailored_resume(db, current_user.id, job_id)
        if not tailored:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Tailored resume not found"
            )
        return tailored
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/tailored/list", response_model=list[TailoredResumeResponse])
def list_tailored_resumes(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all tailored resumes for user"""
    try:
        total, tailored = TailoringService.get_user_tailored_resumes(
            db, current_user.id, skip, limit
        )
        return tailored
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/tailored/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tailored_resume(
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete tailored resume"""
    try:
        TailoringService.delete_tailored_resume(db, current_user.id, job_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
