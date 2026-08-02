"""
Resume management API endpoints
"""

import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, Header, UploadFile, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import SecurityService
from app.models.resume import Resume
from app.schemas.resume import (
    ResumeListResponse,
    ResumeResponse,
    ResumeSetActiveRequest,
    ResumeUploadResponse,
)
from app.services.resume_service import ResumeService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/resumes",
    tags=["resumes"],
)


def get_current_user_id(
    authorization: Annotated[str, Header()] = None,
    db: Session = Depends(get_db),
) -> UUID:
    """
    Extract and verify current user from authorization header

    Args:
        authorization: Authorization header (Bearer <token>)
        db: Database session

    Returns:
        User ID

    Raises:
        HTTPException: If not authenticated
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = authorization.split(" ")[1]
    user_id_str = SecurityService.verify_token(token, token_type="access")

    if user_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format",
        )

    return user_id


@router.post("/upload", response_model=ResumeUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(..., description="PDF resume file"),
    authorization: Annotated[str, Header()] = None,
    db: Session = Depends(get_db),
) -> ResumeUploadResponse:
    """
    Upload a PDF resume

    Args:
        file: Uploaded PDF file
        authorization: Authorization header
        db: Database session

    Returns:
        Upload response with resume ID

    Raises:
        HTTPException: If validation fails or upload fails
    """
    try:
        # Get current user
        user_id = get_current_user_id(authorization, db)

        # Validate file type and extension
        if not file.filename or not file.filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="Only PDF files are accepted",
            )

        # Read file content
        file_content = await file.read()

        # Create resume record
        resume = ResumeService.create_resume(
            db=db,
            user_id=user_id,
            file_content=file_content,
            original_filename=file.filename,
            mime_type=file.content_type or "application/pdf",
        )

        logger.info(f"Resume uploaded by user {user_id}: {resume.id}")

        return ResumeUploadResponse(
            id=resume.id,
            filename=resume.filename,
            original_filename=resume.original_filename,
            file_size=resume.file_size,
            uploaded_at=resume.uploaded_at,
            message="Resume uploaded successfully",
        )

    except HTTPException:
        raise
    except ValueError as e:
        error_msg = str(e)
        logger.warning(f"Resume upload validation error: {error_msg}")
        
        # Return appropriate HTTP status codes based on error message
        if "File too large" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File exceeds maximum size of 10MB",
            )
        elif "Invalid file type" in error_msg or "Only PDF" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="Only PDF files are accepted",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg,
            )
    except Exception as e:
        logger.error(f"Resume upload error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload resume. Please try again.",
        )


@router.get("/", response_model=ResumeListResponse)
async def list_resumes(
    authorization: Annotated[str, Header()] = None,
    db: Session = Depends(get_db),
    include_inactive: bool = False,
) -> ResumeListResponse:
    """
    List all resumes for the current user

    Args:
        authorization: Authorization header
        db: Database session
        include_inactive: Whether to include inactive resumes

    Returns:
        List of resumes
    """
    try:
        # Get current user
        user_id = get_current_user_id(authorization, db)

        # Get resumes
        resumes = ResumeService.get_user_resumes(
            db=db,
            user_id=user_id,
            include_inactive=include_inactive,
        )

        return ResumeListResponse(
            resumes=[ResumeResponse.model_validate(r) for r in resumes],
            total=len(resumes),
        )

    except Exception as e:
        logger.error(f"Error listing resumes: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch resumes",
        )


@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume(
    resume_id: UUID,
    authorization: Annotated[str, Header()] = None,
    db: Session = Depends(get_db),
) -> ResumeResponse:
    """
    Get a specific resume by ID

    Args:
        resume_id: Resume ID
        authorization: Authorization header
        db: Database session

    Returns:
        Resume details

    Raises:
        HTTPException: If resume not found
    """
    try:
        # Get current user
        user_id = get_current_user_id(authorization, db)

        # Get resume
        resume = ResumeService.get_resume_by_id(db, resume_id, user_id)
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found",
            )

        return ResumeResponse.model_validate(resume)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching resume {resume_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch resume",
        )


@router.post("/{resume_id}/set-active", response_model=ResumeResponse)
async def set_active_resume(
    resume_id: UUID,
    authorization: Annotated[str, Header()] = None,
    db: Session = Depends(get_db),
) -> ResumeResponse:
    """
    Set a resume as the active resume

    Args:
        resume_id: Resume ID to activate
        authorization: Authorization header
        db: Database session

    Returns:
        Updated resume

    Raises:
        HTTPException: If resume not found
    """
    try:
        # Get current user
        user_id = get_current_user_id(authorization, db)

        # Set as active
        resume = ResumeService.set_active_resume(db, resume_id, user_id)

        logger.info(f"Resume {resume_id} set as active for user {user_id}")

        return ResumeResponse.model_validate(resume)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error setting active resume: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update resume status",
        )


@router.delete("/{resume_id}", status_code=status.HTTP_200_OK)
async def delete_resume(
    resume_id: UUID,
    authorization: Annotated[str, Header()] = None,
    db: Session = Depends(get_db),
) -> dict:
    """
    Delete a resume

    Args:
        resume_id: Resume ID to delete
        authorization: Authorization header
        db: Database session

    Returns:
        Success message
    """
    try:
        # Get current user
        user_id = get_current_user_id(authorization, db)

        # Delete resume
        ResumeService.delete_resume(db, resume_id, user_id)

        logger.info(f"Resume {resume_id} deleted for user {user_id}")

        return {"message": "Resume deleted successfully"}

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error deleting resume: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete resume",
        )
