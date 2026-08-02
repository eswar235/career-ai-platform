"""
Browser automation API routes
"""

import logging
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Query

from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.automation import (
    AutomationJobCreate,
    AutomationJobResponse,
    AutomationJobDetailResponse,
    StartAutomationRequest,
    AutomationStatusResponse,
    AutomationStepCreate,
    AutomationStepResponse,
    BulkAutomationRequest,
    BulkAutomationResponse,
)
from app.services.automation_service import AutomationService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/automation", tags=["automation"])


# ========== Automation Job Endpoints ==========

@router.post("", response_model=AutomationJobResponse)
def create_automation_job(
    request: AutomationJobCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new automation job"""
    try:
        job = AutomationService.create_automation_job(
            db=db,
            user_id=current_user.id,
            job_id=request.job_id,
            job_url=request.job_url,
            automation_type=request.automation_type,
            browser_type=request.browser_type,
            headless=request.headless,
            max_retries=request.max_retries,
        )
        return job
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating automation job: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create automation job",
        )


@router.get("/{automation_id}", response_model=AutomationJobDetailResponse)
def get_automation_job(
    automation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get automation job details"""
    try:
        job = AutomationService.get_automation_job(db, automation_id)
        if not job or job.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Automation job not found",
            )
        return job
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving automation job: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve automation job",
        )


@router.get("", response_model=list[AutomationJobResponse])
def list_automation_jobs(
    status: str = Query(None, description="Filter by status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List user's automation jobs"""
    try:
        total, jobs = AutomationService.get_user_automation_jobs(
            db, current_user.id, status, skip, limit
        )
        return jobs
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error listing automation jobs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list automation jobs",
        )


@router.post("/{automation_id}/start", response_model=AutomationStatusResponse)
def start_automation_job(
    automation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Start an automation job"""
    try:
        job = AutomationService.get_automation_job(db, automation_id)
        if not job or job.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Automation job not found",
            )

        # Update status to in_progress
        AutomationService.update_automation_job_status(
            db, automation_id, "in_progress"
        )

        AutomationService.add_automation_log(
            db, automation_id, "INFO", "Automation job started"
        )

        return AutomationStatusResponse(
            automation_id=automation_id,
            status="in_progress",
            current_step=0,
            total_steps=len(job.steps),
            progress=0.0,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting automation job: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start automation job",
        )


@router.post("/{automation_id}/stop", response_model=AutomationStatusResponse)
def stop_automation_job(
    automation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Stop an automation job"""
    try:
        job = AutomationService.get_automation_job(db, automation_id)
        if not job or job.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Automation job not found",
            )

        AutomationService.update_automation_job_status(
            db, automation_id, "paused"
        )

        AutomationService.add_automation_log(
            db, automation_id, "INFO", "Automation job stopped"
        )

        return AutomationStatusResponse(
            automation_id=automation_id,
            status="paused",
            current_step=0,
            total_steps=len(job.steps),
            progress=0.0,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error stopping automation job: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to stop automation job",
        )


@router.get("/{automation_id}/status", response_model=AutomationStatusResponse)
def get_automation_status(
    automation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get automation job status"""
    try:
        job = AutomationService.get_automation_job(db, automation_id)
        if not job or job.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Automation job not found",
            )

        steps = AutomationService.get_automation_steps(db, automation_id)
        completed_steps = sum(1 for s in steps if s.success)
        total_steps = len(steps)
        progress = (completed_steps / total_steps * 100) if total_steps > 0 else 0

        return AutomationStatusResponse(
            automation_id=automation_id,
            status=job.status,
            current_step=completed_steps,
            total_steps=total_steps,
            progress=progress,
            error_message=job.error_message,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting automation status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get automation status",
        )


@router.post("/{automation_id}/steps", response_model=AutomationStepResponse)
def add_automation_step(
    automation_id: uuid.UUID,
    request: AutomationStepCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add a step to automation job"""
    try:
        job = AutomationService.get_automation_job(db, automation_id)
        if not job or job.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Automation job not found",
            )

        step = AutomationService.add_automation_step(
            db=db,
            automation_id=automation_id,
            step_order=request.step_order,
            action_type=request.action_type,
            step_name=request.step_name,
            selector=request.selector,
            value=request.value,
            wait_time_ms=request.wait_time_ms,
            retry_on_fail=request.retry_on_fail,
        )
        return step
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error adding automation step: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add automation step",
        )


@router.get("/{automation_id}/steps", response_model=list[AutomationStepResponse])
def get_automation_steps(
    automation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get steps for automation job"""
    try:
        job = AutomationService.get_automation_job(db, automation_id)
        if not job or job.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Automation job not found",
            )

        steps = AutomationService.get_automation_steps(db, automation_id)
        return steps
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving automation steps: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve automation steps",
        )


@router.post("/bulk", response_model=BulkAutomationResponse)
def create_bulk_automation(
    request: BulkAutomationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create automation jobs for multiple jobs"""
    try:
        created = 0
        failed = 0
        automation_ids = []

        for job_id in request.job_ids:
            try:
                job = AutomationService.create_automation_job(
                    db=db,
                    user_id=current_user.id,
                    job_id=job_id,
                    job_url="",  # Would be populated from job details
                    automation_type=request.automation_type,
                    browser_type=request.browser_type,
                    headless=request.headless,
                    max_retries=request.max_retries,
                )
                automation_ids.append(job.id)
                created += 1
            except Exception as e:
                logger.warning(f"Failed to create automation for job {job_id}: {str(e)}")
                failed += 1

        return BulkAutomationResponse(
            created=created,
            failed=failed,
            status="created",
            automation_ids=automation_ids,
        )
    except Exception as e:
        logger.error(f"Error in bulk automation creation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create bulk automation",
        )


@router.delete("/{automation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_automation_job(
    automation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete an automation job"""
    try:
        job = AutomationService.get_automation_job(db, automation_id)
        if not job or job.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Automation job not found",
            )

        AutomationService.delete_automation_job(db, automation_id)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error deleting automation job: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete automation job",
        )
