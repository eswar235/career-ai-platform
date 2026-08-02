"""
Job application tracking API routes
"""

import logging
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Query

from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.application import (
    JobApplicationCreate,
    JobApplicationUpdate,
    JobApplicationResponse,
    JobApplicationDetailResponse,
    InterviewCreate,
    InterviewUpdate,
    InterviewResponse,
    JobOfferCreate,
    JobOfferUpdate,
    JobOfferResponse,
    BulkStatusUpdateRequest,
    BulkStatusUpdateResponse,
)
from app.services.application_service import ApplicationService
from app.services.interview_service import InterviewService
from app.services.offer_service import OfferService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/applications", tags=["applications"])


# ========== Application Endpoints ==========

@router.post("", response_model=JobApplicationResponse)
def create_application(
    request: JobApplicationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new job application"""
    try:
        application = ApplicationService.create_application(
            db=db,
            user_id=current_user.id,
            job_id=request.job_id,
            applied_via=request.applied_via,
            cover_letter_id=request.cover_letter_id,
            resume_id=request.resume_id,
            notes=request.notes,
        )
        return application
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating application: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create application",
        )


@router.get("/{application_id}", response_model=JobApplicationDetailResponse)
def get_application(
    application_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific application"""
    try:
        application = ApplicationService.get_application(db, application_id)
        if not application or application.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found",
            )
        return application
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving application: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve application",
        )


@router.get("", response_model=list[JobApplicationResponse])
def list_applications(
    status: str = Query(None, description="Filter by status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List user's job applications"""
    try:
        total, applications = ApplicationService.get_user_applications(
            db, current_user.id, status, skip, limit
        )
        return applications
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error listing applications: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list applications",
        )


@router.get("/job/{job_id}", response_model=JobApplicationResponse)
def get_application_for_job(
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get application for a specific job"""
    try:
        application = ApplicationService.get_application_for_job(
            db, current_user.id, job_id
        )
        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found",
            )
        return application
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving application: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve application",
        )


@router.put("/{application_id}", response_model=JobApplicationResponse)
def update_application(
    application_id: uuid.UUID,
    request: JobApplicationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update an application"""
    try:
        application = ApplicationService.get_application(db, application_id)
        if not application or application.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found",
            )

        updated = ApplicationService.update_application(db, application_id, request)
        return updated
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating application: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update application",
        )


@router.put("/{application_id}/status", response_model=JobApplicationResponse)
def update_application_status(
    application_id: uuid.UUID,
    new_status: str = Query(..., description="New status"),
    notes: str = Query(None, description="Status change notes"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update application status"""
    try:
        application = ApplicationService.get_application(db, application_id)
        if not application or application.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found",
            )

        updated = ApplicationService.update_application_status(
            db, application_id, new_status, notes
        )
        return updated
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update status",
        )


@router.post("/bulk-update", response_model=BulkStatusUpdateResponse)
def bulk_update_status(
    request: BulkStatusUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Bulk update status for multiple applications"""
    try:
        updated, failed = ApplicationService.bulk_update_status(
            db,
            current_user.id,
            request.application_ids,
            request.new_status,
            request.notes,
        )

        return BulkStatusUpdateResponse(
            updated=updated,
            failed=failed,
            status="completed",
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error in bulk update: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to bulk update",
        )


@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_application(
    application_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete an application"""
    try:
        application = ApplicationService.get_application(db, application_id)
        if not application or application.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found",
            )

        ApplicationService.delete_application(db, application_id)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error deleting application: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete application",
        )


# ========== Interview Endpoints ==========

@router.post("/{application_id}/interviews", response_model=InterviewResponse)
def create_interview(
    application_id: uuid.UUID,
    request: InterviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new interview"""
    try:
        application = ApplicationService.get_application(db, application_id)
        if not application or application.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found",
            )

        interview = InterviewService.create_interview(
            db=db,
            application_id=application_id,
            interview_type=request.interview_type,
            scheduled_date=request.scheduled_date,
            duration_minutes=request.duration_minutes,
            interviewer_name=request.interviewer_name,
            interviewer_email=request.interviewer_email,
            meeting_link=request.meeting_link,
            preparation_notes=request.preparation_notes,
        )
        return interview
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating interview: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create interview",
        )


@router.get("/{application_id}/interviews", response_model=list[InterviewResponse])
def list_interviews(
    application_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List interviews for an application"""
    try:
        application = ApplicationService.get_application(db, application_id)
        if not application or application.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found",
            )

        interviews = InterviewService.get_application_interviews(db, application_id)
        return interviews
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error listing interviews: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list interviews",
        )


@router.put("/interviews/{interview_id}", response_model=InterviewResponse)
def update_interview(
    interview_id: uuid.UUID,
    request: InterviewUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update an interview"""
    try:
        interview = InterviewService.get_interview(db, interview_id)
        if not interview:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview not found",
            )

        application = ApplicationService.get_application(db, interview.application_id)
        if not application or application.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found",
            )

        updated = InterviewService.update_interview(
            db=db,
            interview_id=interview_id,
            interview_type=request.interview_type,
            scheduled_date=request.scheduled_date,
            duration_minutes=request.duration_minutes,
            interviewer_name=request.interviewer_name,
            interviewer_email=request.interviewer_email,
            meeting_link=request.meeting_link,
            preparation_notes=request.preparation_notes,
            status=request.status,
            feedback=request.feedback,
            interview_score=request.interview_score,
        )
        return updated
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating interview: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update interview",
        )


@router.delete("/interviews/{interview_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_interview(
    interview_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete an interview"""
    try:
        interview = InterviewService.get_interview(db, interview_id)
        if not interview:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview not found",
            )

        application = ApplicationService.get_application(db, interview.application_id)
        if not application or application.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found",
            )

        InterviewService.delete_interview(db, interview_id)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error deleting interview: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete interview",
        )


# ========== Offer Endpoints ==========

@router.post("/{application_id}/offers", response_model=JobOfferResponse)
def create_offer(
    application_id: uuid.UUID,
    request: JobOfferCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new job offer"""
    try:
        application = ApplicationService.get_application(db, application_id)
        if not application or application.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found",
            )

        offer = OfferService.create_offer(
            db=db,
            application_id=application_id,
            salary=request.salary,
            start_date=request.start_date,
            bonus=request.bonus,
            benefits=request.benefits,
            offer_letter_url=request.offer_letter_url,
            offer_expiration_date=request.offer_expiration_date,
        )
        return offer
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating offer: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create offer",
        )


@router.get("/{application_id}/offers", response_model=JobOfferResponse)
def get_application_offer(
    application_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get offer for an application"""
    try:
        application = ApplicationService.get_application(db, application_id)
        if not application or application.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found",
            )

        offer = OfferService.get_application_offer(db, application_id)
        if not offer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Offer not found",
            )
        return offer
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error retrieving offer: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve offer",
        )


@router.put("/offers/{offer_id}", response_model=JobOfferResponse)
def update_offer(
    offer_id: uuid.UUID,
    request: JobOfferUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a job offer"""
    try:
        offer = OfferService.get_offer(db, offer_id)
        if not offer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Offer not found",
            )

        application = ApplicationService.get_application(db, offer.application_id)
        if not application or application.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found",
            )

        updated = OfferService.update_offer(
            db=db,
            offer_id=offer_id,
            status=request.status,
            salary=request.salary,
            start_date=request.start_date,
            bonus=request.bonus,
            benefits=request.benefits,
            offer_letter_url=request.offer_letter_url,
            offer_expiration_date=request.offer_expiration_date,
            negotiation_notes=request.negotiation_notes,
        )
        return updated
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating offer: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update offer",
        )


@router.post("/offers/{offer_id}/accept", response_model=JobOfferResponse)
def accept_offer(
    offer_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Accept a job offer"""
    try:
        offer = OfferService.get_offer(db, offer_id)
        if not offer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Offer not found",
            )

        application = ApplicationService.get_application(db, offer.application_id)
        if not application or application.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found",
            )

        updated = OfferService.accept_offer(db, offer_id)
        return updated
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error accepting offer: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to accept offer",
        )


@router.post("/offers/{offer_id}/decline", response_model=JobOfferResponse)
def decline_offer(
    offer_id: uuid.UUID,
    reason: str = Query(None, description="Reason for declining"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Decline a job offer"""
    try:
        offer = OfferService.get_offer(db, offer_id)
        if not offer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Offer not found",
            )

        application = ApplicationService.get_application(db, offer.application_id)
        if not application or application.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found",
            )

        updated = OfferService.decline_offer(db, offer_id, reason)
        return updated
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error declining offer: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to decline offer",
        )


@router.delete("/offers/{offer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_offer(
    offer_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a job offer"""
    try:
        offer = OfferService.get_offer(db, offer_id)
        if not offer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Offer not found",
            )

        application = ApplicationService.get_application(db, offer.application_id)
        if not application or application.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found",
            )

        OfferService.delete_offer(db, offer_id)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error deleting offer: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete offer",
        )
