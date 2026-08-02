"""
Celery tasks for resume parsing
Runs parsing asynchronously in background workers
"""

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from celery import shared_task
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.config import settings
from app.models.parsed_resume import ParsedResume
from app.models.resume import Resume
from app.providers.base import (
    AIProviderError,
    AIProviderRateLimitError,
    AIProviderTimeoutError,
)
from app.providers.openai_provider import OpenAIProvider
from app.providers.base import AIProviderConfig
from app.services.parsing_service import (
    PDFExtractionService,
    ResumeParsingService,
)
from app.services.ocr_service import OCRService, ExtractionMethod
from app.services.storage_service import StorageService

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(AIProviderRateLimitError, AIProviderTimeoutError),
    retry_backoff=True,
    retry_backoff_max=600,  # 10 minutes max
    retry_jitter=True,
)
def parse_resume_task(
    self,
    resume_id: str,
    user_id: str,
) -> dict:
    """
    Asynchronous task to parse a resume

    Args:
        self: Celery task instance
        resume_id: Resume ID to parse
        user_id: User ID for verification

    Returns:
        Dictionary with parsing result
    """
    db = SessionLocal()

    try:
        logger.info(f"Starting parse task for resume {resume_id}")

        # Get resume
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            logger.error(f"Resume not found: {resume_id}")
            return {"status": "failed", "error": "Resume not found"}

        # Verify ownership
        if str(resume.user_id) != str(user_id):
            logger.error(f"Ownership verification failed for resume {resume_id}")
            return {"status": "failed", "error": "Ownership verification failed"}

        # Update status to parsing
        resume.parsing_status = "parsing"
        resume.parsing_error = None
        db.commit()
        logger.info(f"Updated resume {resume_id} status to 'parsing'")

        try:
            # Read file from storage
            file_content = StorageService.get_file_local(resume.storage_path)
            if not file_content:
                raise ValueError("Failed to read resume file")

            # Extract text with pdfplumber
            raw_text = PDFExtractionService.extract_text_from_pdf(file_content)
            extraction_method = ExtractionMethod.PDFPLUMBER

            # Use OCR if needed
            if OCRService.should_use_ocr(raw_text):
                logger.info("Attempting OCR extraction")
                try:
                    ocr_text, _ = OCRService.extract_text_with_ocr(file_content)
                    raw_text, extraction_method = OCRService.compare_extractions(
                        raw_text, ocr_text
                    )
                except Exception as e:
                    logger.warning(f"OCR failed, continuing with pdfplumber: {str(e)}")

            if not raw_text:
                raise ValueError("Failed to extract text from PDF")

            logger.info(f"Extracted text using {extraction_method.value}")

            # Parse with AI
            provider_config = AIProviderConfig(
                api_key=settings.OPENAI_API_KEY,
                model=settings.OPENAI_MODEL,
                max_retries=3,
            )
            provider = OpenAIProvider(provider_config)

            # Run async parsing
            parsed_data = asyncio.run(provider.parse_resume(raw_text))

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
                extraction_method=extraction_method.value,
            )

            # Update resume status
            resume.parsing_status = "completed"
            resume.parsing_error = None
            resume.parsed_at = datetime.now(timezone.utc)
            db.commit()

            logger.info(f"Successfully parsed resume {resume_id}")

            return {
                "status": "completed",
                "parsed_resume_id": str(parsed_resume.id),
                "confidence_score": confidence_score,
            }

        except AIProviderRateLimitError as e:
            # Retry with exponential backoff
            logger.warning(f"Rate limited for resume {resume_id}, retrying...")
            resume.parsing_status = "queued"
            resume.parsing_error = "Rate limited, retrying..."
            resume.retry_count = (resume.retry_count or 0) + 1
            resume.next_retry_time = datetime.now(timezone.utc) + timedelta(
                seconds=min(60 * (2 ** resume.retry_count), 3600)
            )
            db.commit()

            raise self.retry(countdown=min(60 * (2 ** self.request.retries), 3600))

        except AIProviderTimeoutError as e:
            # Retry on timeout
            logger.warning(f"Timeout for resume {resume_id}, retrying...")
            resume.parsing_status = "queued"
            resume.parsing_error = "Timeout, retrying..."
            resume.retry_count = (resume.retry_count or 0) + 1
            resume.next_retry_time = datetime.now(timezone.utc) + timedelta(
                seconds=min(30 * (2 ** resume.retry_count), 600)
            )
            db.commit()

            raise self.retry(countdown=min(30 * (2 ** self.request.retries), 600))

        except Exception as e:
            logger.error(f"Failed to parse resume {resume_id}: {str(e)}")
            resume.parsing_status = "failed"
            resume.parsing_error = str(e)
            resume.retry_count = (resume.retry_count or 0) + 1
            resume.last_error = str(e)
            resume.last_attempt = datetime.now(timezone.utc)
            db.commit()

            return {"status": "failed", "error": str(e), "resume_id": str(resume_id)}

    finally:
        db.close()


@shared_task(bind=True)
def retry_failed_parsing_task(self, resume_id: str) -> dict:
    """
    Retry parsing a failed resume

    Args:
        self: Celery task instance
        resume_id: Resume ID to retry

    Returns:
        Dictionary with retry result
    """
    db = SessionLocal()

    try:
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            return {"status": "failed", "error": "Resume not found"}

        logger.info(f"Retrying parse for resume {resume_id}")

        # Re-queue the parsing task
        parse_resume_task.delay(str(resume.id), str(resume.user_id))

        resume.parsing_status = "queued"
        resume.next_retry_time = None
        db.commit()

        return {"status": "queued", "resume_id": str(resume_id)}

    finally:
        db.close()
