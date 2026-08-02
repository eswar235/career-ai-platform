"""
Cover letter service for CRUD operations
"""

import logging
import uuid
from typing import Optional, Tuple

from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.cover_letter import CoverLetter, LetterTemplate, LetterExport
from app.models.job import Job
from app.schemas.cover_letter import (
    CoverLetterCreate,
    CoverLetterUpdate,
    CoverLetterResponse,
)

logger = logging.getLogger(__name__)


class CoverLetterService:
    """Service for cover letter management"""

    @staticmethod
    def create_cover_letter(
        db: Session,
        user_id: uuid.UUID,
        job_id: uuid.UUID,
        content: str,
        ai_model: Optional[str] = None,
    ) -> CoverLetter:
        """Create a new cover letter"""
        try:
            # Get next version number
            max_version = (
                db.query(CoverLetter)
                .filter(
                    CoverLetter.user_id == user_id,
                    CoverLetter.job_id == job_id,
                )
                .order_by(desc(CoverLetter.version_number))
                .first()
            )
            next_version = (max_version.version_number + 1) if max_version else 1

            cover_letter = CoverLetter(
                user_id=user_id,
                job_id=job_id,
                content=content,
                version_number=next_version,
                is_draft=True,
                ai_model=ai_model,
            )

            db.add(cover_letter)
            db.commit()
            db.refresh(cover_letter)

            logger.info(
                f"Created cover letter for user {user_id}, job {job_id}, version {next_version}"
            )
            return cover_letter
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating cover letter: {str(e)}")
            raise ValueError(f"Failed to create cover letter: {str(e)}")

    @staticmethod
    def get_cover_letter(
        db: Session,
        cover_letter_id: uuid.UUID,
    ) -> Optional[CoverLetter]:
        """Get a cover letter by ID"""
        try:
            return db.query(CoverLetter).filter(CoverLetter.id == cover_letter_id).first()
        except Exception as e:
            logger.error(f"Error retrieving cover letter: {str(e)}")
            raise ValueError(f"Failed to retrieve cover letter: {str(e)}")

    @staticmethod
    def get_cover_letter_for_job(
        db: Session,
        user_id: uuid.UUID,
        job_id: uuid.UUID,
    ) -> Optional[CoverLetter]:
        """Get the latest cover letter for a job"""
        try:
            return (
                db.query(CoverLetter)
                .filter(
                    CoverLetter.user_id == user_id,
                    CoverLetter.job_id == job_id,
                )
                .order_by(desc(CoverLetter.version_number))
                .first()
            )
        except Exception as e:
            logger.error(f"Error retrieving cover letter for job: {str(e)}")
            raise ValueError(f"Failed to retrieve cover letter: {str(e)}")

    @staticmethod
    def update_cover_letter(
        db: Session,
        cover_letter_id: uuid.UUID,
        update_data: CoverLetterUpdate,
    ) -> CoverLetter:
        """Update a cover letter"""
        try:
            cover_letter = db.query(CoverLetter).filter(CoverLetter.id == cover_letter_id).first()
            if not cover_letter:
                raise ValueError("Cover letter not found")

            if update_data.content:
                cover_letter.content = update_data.content
            if update_data.is_draft is not None:
                cover_letter.is_draft = update_data.is_draft
            if update_data.custom_edits is not None:
                cover_letter.custom_edits = update_data.custom_edits

            db.commit()
            db.refresh(cover_letter)

            logger.info(f"Updated cover letter {cover_letter_id}")
            return cover_letter
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating cover letter: {str(e)}")
            raise ValueError(f"Failed to update cover letter: {str(e)}")

    @staticmethod
    def publish_cover_letter(
        db: Session,
        cover_letter_id: uuid.UUID,
    ) -> CoverLetter:
        """Publish a cover letter (mark as not draft)"""
        try:
            cover_letter = db.query(CoverLetter).filter(CoverLetter.id == cover_letter_id).first()
            if not cover_letter:
                raise ValueError("Cover letter not found")

            cover_letter.is_draft = False
            db.commit()
            db.refresh(cover_letter)

            logger.info(f"Published cover letter {cover_letter_id}")
            return cover_letter
        except Exception as e:
            db.rollback()
            logger.error(f"Error publishing cover letter: {str(e)}")
            raise ValueError(f"Failed to publish cover letter: {str(e)}")

    @staticmethod
    def list_cover_letters(
        db: Session,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 20,
    ) -> Tuple[int, list[CoverLetter]]:
        """List user's cover letters"""
        try:
            query = db.query(CoverLetter).filter(CoverLetter.user_id == user_id)
            total = query.count()

            letters = (
                query.order_by(desc(CoverLetter.created_at))
                .offset(skip)
                .limit(limit)
                .all()
            )

            return total, letters
        except Exception as e:
            logger.error(f"Error listing cover letters: {str(e)}")
            raise ValueError(f"Failed to list cover letters: {str(e)}")

    @staticmethod
    def delete_cover_letter(
        db: Session,
        cover_letter_id: uuid.UUID,
    ) -> None:
        """Delete a cover letter"""
        try:
            cover_letter = db.query(CoverLetter).filter(CoverLetter.id == cover_letter_id).first()
            if not cover_letter:
                raise ValueError("Cover letter not found")

            db.delete(cover_letter)
            db.commit()

            logger.info(f"Deleted cover letter {cover_letter_id}")
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting cover letter: {str(e)}")
            raise ValueError(f"Failed to delete cover letter: {str(e)}")

    @staticmethod
    def get_cover_letter_versions(
        db: Session,
        user_id: uuid.UUID,
        job_id: uuid.UUID,
    ) -> list[CoverLetter]:
        """Get all versions of a cover letter for a job"""
        try:
            return (
                db.query(CoverLetter)
                .filter(
                    CoverLetter.user_id == user_id,
                    CoverLetter.job_id == job_id,
                )
                .order_by(desc(CoverLetter.version_number))
                .all()
            )
        except Exception as e:
            logger.error(f"Error retrieving cover letter versions: {str(e)}")
            raise ValueError(f"Failed to retrieve cover letter versions: {str(e)}")
