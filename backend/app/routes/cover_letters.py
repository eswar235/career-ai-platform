"""
Cover letter API routes
"""

import logging
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Query

from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.cover_letter import (
    CoverLetterCreate,
    CoverLetterUpdate,
    CoverLetterResponse,
    CoverLetterDetailResponse,
    LetterTemplateCreate,
    LetterTemplateUpdate,
    LetterTemplateResponse,
    LetterExportResponse,
    GenerateCoverLetterRequest,
    GenerateCoverLetterResponse,
    BatchGenerateCoverLettersRequest,
    BatchGenerateCoverLettersResponse,
    PublishCoverLetterRequest,
    PublishCoverLetterResponse,
)
from app.services.cover_letter_service import CoverLetterService
from app.services.generation_service import GenerationService
from app.services.template_service import TemplateService
from app.services.export_service import ExportService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/cover-letters", tags=["cover-letters"])


# Cover Letter Endpoints
@router.post("/generate", response_model=GenerateCoverLetterResponse)
def generate_cover_letter(
    request: GenerateCoverLetterRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Generate a new cover letter using AI"""
    try:
        # Generate content
        content = GenerationService.generate_cover_letter(
            db=db,
            user_id=current_user.id,
            job_id=request.job_id,
            template_id=request.template_id,
            use_profile=request.use_profile,
        )

        # Save to database
        cover_letter = CoverLetterService.create_cover_letter(
            db=db,
            user_id=current_user.id,
            job_id=request.job_id,
            content=content,
            ai_model="gpt-3.5-turbo",
        )

        return GenerateCoverLetterResponse(
            id=cover_letter.id,
            content=cover_letter.content,
            version_number=cover_letter.version_number,
            generated_at=cover_letter.generated_at,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating cover letter: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate cover letter",
        )


@router.post("/batch-generate", response_model=BatchGenerateCoverLettersResponse)
def batch_generate_cover_letters(
    request: BatchGenerateCoverLettersRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Generate cover letters for multiple jobs"""
    try:
        count = GenerationService.generate_multiple_cover_letters(
            db=db,
            user_id=current_user.id,
            job_ids=request.job_ids,
        )

        return BatchGenerateCoverLettersResponse(
            generated=count,
            job_ids=request.job_ids,
            timestamp=__import__("datetime").datetime.utcnow(),
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error in batch generation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate cover letters",
        )


@router.get("/{letter_id}", response_model=CoverLetterDetailResponse)
def get_cover_letter(
    letter_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific cover letter"""
    try:
        letter = CoverLetterService.get_cover_letter(db, letter_id)
        if not letter or letter.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cover letter not found",
            )
        return letter
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving cover letter: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve cover letter",
        )


@router.get("/job/{job_id}", response_model=CoverLetterResponse)
def get_cover_letter_for_job(
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get the latest cover letter for a job"""
    try:
        letter = CoverLetterService.get_cover_letter_for_job(db, current_user.id, job_id)
        if not letter:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cover letter not found",
            )
        return letter
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving cover letter for job: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve cover letter",
        )


@router.put("/{letter_id}", response_model=CoverLetterResponse)
def update_cover_letter(
    letter_id: uuid.UUID,
    request: CoverLetterUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a cover letter"""
    try:
        letter = CoverLetterService.get_cover_letter(db, letter_id)
        if not letter or letter.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cover letter not found",
            )

        updated_letter = CoverLetterService.update_cover_letter(db, letter_id, request)
        return updated_letter
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating cover letter: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update cover letter",
        )


@router.post("/{letter_id}/publish", response_model=PublishCoverLetterResponse)
def publish_cover_letter(
    letter_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Publish a cover letter (mark as final)"""
    try:
        letter = CoverLetterService.get_cover_letter(db, letter_id)
        if not letter or letter.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cover letter not found",
            )

        published_letter = CoverLetterService.publish_cover_letter(db, letter_id)
        return PublishCoverLetterResponse(
            id=published_letter.id,
            is_draft=published_letter.is_draft,
            published_at=published_letter.updated_at,
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error publishing cover letter: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to publish cover letter",
        )


@router.get("", response_model=list[CoverLetterResponse])
def list_cover_letters(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List user's cover letters"""
    try:
        total, letters = CoverLetterService.list_cover_letters(
            db, current_user.id, skip, limit
        )
        return letters
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error listing cover letters: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list cover letters",
        )


@router.delete("/{letter_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cover_letter(
    letter_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a cover letter"""
    try:
        letter = CoverLetterService.get_cover_letter(db, letter_id)
        if not letter or letter.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cover letter not found",
            )

        CoverLetterService.delete_cover_letter(db, letter_id)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error deleting cover letter: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete cover letter",
        )


@router.get("/{letter_id}/versions", response_model=list[CoverLetterResponse])
def get_cover_letter_versions(
    letter_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all versions of a cover letter"""
    try:
        # Get the letter to verify ownership
        letter = CoverLetterService.get_cover_letter(db, letter_id)
        if not letter or letter.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cover letter not found",
            )

        versions = CoverLetterService.get_cover_letter_versions(
            db, current_user.id, letter.job_id
        )
        return versions
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving versions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve versions",
        )


# Template Endpoints
@router.post("/templates", response_model=LetterTemplateResponse)
def create_template(
    request: LetterTemplateCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new letter template"""
    try:
        template = TemplateService.create_template(db, current_user.id, request)
        return template
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create template",
        )


@router.get("/templates", response_model=list[LetterTemplateResponse])
def list_templates(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List user's templates"""
    try:
        total, templates = TemplateService.list_templates(db, current_user.id, skip, limit)
        return templates
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error listing templates: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list templates",
        )


@router.get("/templates/{template_id}", response_model=LetterTemplateResponse)
def get_template(
    template_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific template"""
    try:
        template = TemplateService.get_template(db, template_id)
        if not template or template.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found",
            )
        return template
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve template",
        )


@router.put("/templates/{template_id}", response_model=LetterTemplateResponse)
def update_template(
    template_id: uuid.UUID,
    request: LetterTemplateUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a template"""
    try:
        updated_template = TemplateService.update_template(
            db, template_id, current_user.id, request
        )
        return updated_template
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update template",
        )


@router.delete("/templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_template(
    template_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a template"""
    try:
        TemplateService.delete_template(db, template_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error deleting template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete template",
        )


# Export Endpoints
@router.post("/{letter_id}/export/pdf", response_model=LetterExportResponse)
def export_as_pdf(
    letter_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Export cover letter as PDF"""
    try:
        letter = CoverLetterService.get_cover_letter(db, letter_id)
        if not letter or letter.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cover letter not found",
            )

        export = ExportService.export_as_pdf(db, letter_id)
        return export
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error exporting as PDF: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export as PDF",
        )


@router.post("/{letter_id}/export/docx", response_model=LetterExportResponse)
def export_as_docx(
    letter_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Export cover letter as DOCX"""
    try:
        letter = CoverLetterService.get_cover_letter(db, letter_id)
        if not letter or letter.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cover letter not found",
            )

        export = ExportService.export_as_docx(db, letter_id)
        return export
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error exporting as DOCX: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export as DOCX",
        )


@router.post("/{letter_id}/export/txt", response_model=LetterExportResponse)
def export_as_txt(
    letter_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Export cover letter as TXT"""
    try:
        letter = CoverLetterService.get_cover_letter(db, letter_id)
        if not letter or letter.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cover letter not found",
            )

        export = ExportService.export_as_text(db, letter_id)
        return export
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error exporting as TXT: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export as TXT",
        )


@router.get("/{letter_id}/exports", response_model=list[LetterExportResponse])
def get_exports(
    letter_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all exports for a cover letter"""
    try:
        letter = CoverLetterService.get_cover_letter(db, letter_id)
        if not letter or letter.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cover letter not found",
            )

        exports = ExportService.get_exports(db, letter_id)
        return exports
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error retrieving exports: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve exports",
        )
