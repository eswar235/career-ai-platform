"""
Resume parsing API endpoints
"""

import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import SecurityService
from app.models.resume import Resume
from app.schemas.parsing import (
    ParsedResumeResponse,
    ParsedResumeUpdate,
    ParseResumeResponse,
)
from app.services.parsing_service import (
    PDFExtractionService,
    ResumeParsingService,
)
from app.services.resume_service import ResumeService
from app.services.storage_service import StorageService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/parsing",
    tags=["parsing"],
)


def get_current_user_id(
    authorization: Annotated[str, Header()] = None,
    db: Session = Depends(get_db),
) -> UUID:
    """Extract and verify current user from authorization header"""
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


@router.post("/parse/{resume_id}", response_model=ParseResumeResponse)
async def parse_resume(
    resume_id: UUID,
    authorization: Annotated[str, Header()] = None,
    db: Session = Depends(get_db),
) -> ParseResumeResponse:
    """
    Parse a resume and extract structured data

    Args:
        resume_id: Resume ID to parse
        authorization: Authorization header
        db: Database session

    Returns:
        Parse response with extracted data
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

        # Update status to processing
        ResumeService.update_parsing_status(db, resume_id, "processing")

        try:
            # Read file from storage
            file_content = StorageService.get_file_local(resume.storage_path)
            if not file_content:
                raise ValueError("Failed to read resume file")

            # Extract text from PDF
            raw_text = PDFExtractionService.extract_text_from_pdf(file_content)
            if not raw_text:
                raise ValueError("Failed to extract text from PDF")

            # Parse with AI (requires OpenAI API key)
            if not settings.OPENAI_API_KEY:
                raise ValueError(
                    "OpenAI API key not configured. Set OPENAI_API_KEY in environment."
                )

            from openai import OpenAI

            client = OpenAI(api_key=settings.OPENAI_API_KEY)

            parsed_data = ResumeParsingService.parse_resume_with_ai(raw_text, client)
            if not parsed_data:
                raise ValueError("Failed to parse resume with AI")

            # Calculate confidence score
            confidence_score = ResumeParsingService.calculate_confidence_score(
                parsed_data, raw_text
            )

            # Create ParsedResume record
            parsed_resume = ResumeParsingService.create_parsed_resume(
                db=db,
                resume_id=resume_id,
                user_id=user_id,
                parsed_data=parsed_data,
                raw_text=raw_text,
                confidence_score=confidence_score,
            )

            # Update resume status
            ResumeService.update_parsing_status(db, resume_id, "completed")

            logger.info(f"Successfully parsed resume {resume_id}")

            return ParseResumeResponse(
                parsed_resume_id=parsed_resume.id,
                resume_id=resume_id,
                full_name=parsed_resume.full_name,
                email=parsed_resume.email,
                confidence_score=confidence_score,
                message="Resume parsed successfully",
            )

        except Exception as e:
            # Update status to failed
            error_msg = str(e)
            ResumeService.update_parsing_status(db, resume_id, "failed", error_msg)
            logger.error(f"Failed to parse resume {resume_id}: {error_msg}")
            raise

    except HTTPException:
        raise
    except ValueError as e:
        logger.warning(f"Resume parsing validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Resume parsing error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to parse resume. Please try again.",
        )


@router.get("/parsed/{resume_id}", response_model=ParsedResumeResponse)
async def get_parsed_resume(
    resume_id: UUID,
    authorization: Annotated[str, Header()] = None,
    db: Session = Depends(get_db),
) -> ParsedResumeResponse:
    """
    Get parsed resume data

    Args:
        resume_id: Resume ID
        authorization: Authorization header
        db: Database session

    Returns:
        Parsed resume data
    """
    try:
        # Get current user
        user_id = get_current_user_id(authorization, db)

        # Get parsed resume
        from app.models.parsed_resume import ParsedResume

        parsed_resume = (
            db.query(ParsedResume)
            .filter(
                ParsedResume.resume_id == resume_id,
                ParsedResume.user_id == user_id,
            )
            .first()
        )

        if not parsed_resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parsed resume not found",
            )

        return ParsedResumeResponse.model_validate(parsed_resume)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching parsed resume: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch parsed resume",
        )


@router.put("/parsed/{parsed_resume_id}", response_model=ParsedResumeResponse)
async def update_parsed_resume(
    parsed_resume_id: UUID,
    updates: ParsedResumeUpdate,
    authorization: Annotated[str, Header()] = None,
    db: Session = Depends(get_db),
) -> ParsedResumeResponse:
    """
    Update parsed resume with user corrections

    Args:
        parsed_resume_id: ParsedResume ID
        updates: Fields to update
        authorization: Authorization header
        db: Database session

    Returns:
        Updated parsed resume
    """
    try:
        # Get current user
        user_id = get_current_user_id(authorization, db)

        # Verify ownership
        from app.models.parsed_resume import ParsedResume

        parsed_resume = (
            db.query(ParsedResume)
            .filter(ParsedResume.id == parsed_resume_id, ParsedResume.user_id == user_id)
            .first()
        )

        if not parsed_resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parsed resume not found",
            )

        # Update with provided fields
        update_data = updates.model_dump(exclude_unset=True)
        updated_resume = ResumeParsingService.update_parsed_resume(
            db, parsed_resume_id, update_data
        )

        logger.info(f"Updated parsed resume {parsed_resume_id}")

        return ParsedResumeResponse.model_validate(updated_resume)

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error updating parsed resume: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update parsed resume",
        )


@router.post("/parsed/{parsed_resume_id}/confirm")
async def confirm_parsed_resume(
    parsed_resume_id: UUID,
    authorization: Annotated[str, Header()] = None,
    db: Session = Depends(get_db),
) -> dict:
    """
    Confirm parsed resume (user reviewed and approved)

    Args:
        parsed_resume_id: ParsedResume ID
        authorization: Authorization header
        db: Database session

    Returns:
        Confirmation message
    """
    try:
        # Get current user
        user_id = get_current_user_id(authorization, db)

        # Verify ownership
        from app.models.parsed_resume import ParsedResume

        parsed_resume = (
            db.query(ParsedResume)
            .filter(ParsedResume.id == parsed_resume_id, ParsedResume.user_id == user_id)
            .first()
        )

        if not parsed_resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parsed resume not found",
            )

        # Confirm parsing
        ResumeParsingService.confirm_parsed_resume(db, parsed_resume_id)

        logger.info(f"Confirmed parsed resume {parsed_resume_id}")

        return {"message": "Parsed resume confirmed successfully"}

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error confirming parsed resume: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to confirm parsed resume",
        )
