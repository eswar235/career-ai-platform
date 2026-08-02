"""
Resume service for handling resume uploads, storage, and management
"""

import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy.orm import Session

from app.models.resume import Resume
from app.schemas.resume import ResumeCreate, ResumeResponse
from app.services.storage_service import StorageService

logger = logging.getLogger(__name__)


class ResumeService:
    """Service for managing resumes"""

    @staticmethod
    def create_resume(
        db: Session,
        user_id: uuid.UUID,
        file_content: bytes,
        original_filename: str,
        mime_type: str = "application/pdf",
        version: str | None = None,
    ) -> Resume:
        """
        Create a new resume record after file validation and storage

        Args:
            db: Database session
            user_id: User ID
            file_content: File content as bytes
            original_filename: Original filename
            mime_type: MIME type
            version: Optional version label

        Returns:
            Created Resume object

        Raises:
            ValueError: If file validation fails or storage fails
        """
        # Check resume count limit (max 5 per user)
        resume_count = db.query(Resume).filter(Resume.user_id == user_id).count()
        if resume_count >= 5:
            logger.warning(f"Resume limit exceeded for user {user_id}")
            raise ValueError("Maximum number of resumes (5) already uploaded. Please delete an existing resume before uploading a new one.")

        # Validate file
        file_size = len(file_content)
        is_valid, error_msg = StorageService.validate_file(
            original_filename,
            file_size,
            mime_type,
        )
        if not is_valid:
            logger.warning(f"File validation failed for user {user_id}: {error_msg}")
            raise ValueError(error_msg)

        # Generate storage path
        storage_path = StorageService.generate_storage_filename(user_id, original_filename)

        # Save file
        saved = StorageService.save_file_local(file_content, storage_path)
        if not saved:
            logger.error(f"Failed to save file for user {user_id}")
            raise ValueError("Failed to save file. Please try again.")

        # Set previously active resumes to inactive (keep only one active)
        if version is None:
            db.query(Resume).filter(
                Resume.user_id == user_id,
                Resume.is_active == True,
            ).update({Resume.is_active: False})

        # Create resume record
        resume = Resume(
            user_id=user_id,
            filename=Path(storage_path).name,
            original_filename=original_filename,
            file_size=file_size,
            storage_path=storage_path,
            mime_type=mime_type,
            version=version,
            is_active=True,
            parsing_status="pending",
        )

        db.add(resume)
        db.commit()
        db.refresh(resume)

        logger.info(f"Resume created for user {user_id}: {resume.id}")
        return resume

    @staticmethod
    def get_resume_by_id(
        db: Session,
        resume_id: uuid.UUID,
        user_id: uuid.UUID | None = None,
    ) -> Resume | None:
        """
        Get resume by ID, optionally filtered by user

        Args:
            db: Database session
            resume_id: Resume ID
            user_id: Optional user ID to verify ownership

        Returns:
            Resume object or None if not found
        """
        query = db.query(Resume).filter(Resume.id == resume_id)

        if user_id:
            query = query.filter(Resume.user_id == user_id)

        return query.first()

    @staticmethod
    def get_user_resumes(
        db: Session,
        user_id: uuid.UUID,
        include_inactive: bool = False,
    ) -> list[Resume]:
        """
        Get all resumes for a user

        Args:
            db: Database session
            user_id: User ID
            include_inactive: Whether to include inactive resumes

        Returns:
            List of Resume objects
        """
        query = db.query(Resume).filter(Resume.user_id == user_id)

        if not include_inactive:
            query = query.filter(Resume.is_active == True)

        return query.order_by(Resume.uploaded_at.desc()).all()

    @staticmethod
    def get_active_resume(
        db: Session,
        user_id: uuid.UUID,
    ) -> Resume | None:
        """
        Get the active resume for a user

        Args:
            db: Database session
            user_id: User ID

        Returns:
            Active Resume object or None
        """
        return (
            db.query(Resume)
            .filter(
                Resume.user_id == user_id,
                Resume.is_active == True,
            )
            .first()
        )

    @staticmethod
    def set_active_resume(
        db: Session,
        resume_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> Resume:
        """
        Set a specific resume as active (deactivates others)

        Args:
            db: Database session
            resume_id: Resume ID to activate
            user_id: User ID for verification

        Returns:
            Updated Resume object

        Raises:
            ValueError: If resume not found or doesn't belong to user
        """
        # Get the resume
        resume = ResumeService.get_resume_by_id(db, resume_id, user_id)
        if not resume:
            raise ValueError("Resume not found or does not belong to this user")

        # Deactivate all other resumes
        db.query(Resume).filter(
            Resume.user_id == user_id,
            Resume.id != resume_id,
        ).update({Resume.is_active: False})

        # Activate this resume
        resume.is_active = True
        db.commit()
        db.refresh(resume)

        logger.info(f"Resume {resume_id} set as active for user {user_id}")
        return resume

    @staticmethod
    def delete_resume(
        db: Session,
        resume_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> bool:
        """
        Delete a resume (soft delete by marking as inactive)

        Args:
            db: Database session
            resume_id: Resume ID
            user_id: User ID for verification

        Returns:
            True if successful

        Raises:
            ValueError: If resume not found or doesn't belong to user
        """
        # Get the resume
        resume = ResumeService.get_resume_by_id(db, resume_id, user_id)
        if not resume:
            raise ValueError("Resume not found or does not belong to this user")

        # Delete file from storage
        StorageService.delete_file_local(resume.storage_path)

        # Delete from database
        db.delete(resume)
        db.commit()

        logger.info(f"Resume {resume_id} deleted for user {user_id}")
        return True

    @staticmethod
    def update_parsing_status(
        db: Session,
        resume_id: uuid.UUID,
        status: str,
        error: str | None = None,
    ) -> Resume:
        """
        Update parsing status of a resume

        Args:
            db: Database session
            resume_id: Resume ID
            status: Parsing status (pending, processing, completed, failed)
            error: Error message if failed

        Returns:
            Updated Resume object
        """
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            raise ValueError("Resume not found")

        resume.parsing_status = status
        resume.parsing_error = error

        if status == "completed":
            resume.parsed_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(resume)

        return resume

    @staticmethod
    def get_resume_by_id_no_user_check(
        db: Session,
        resume_id: uuid.UUID,
    ) -> Resume | None:
        """
        Get resume by ID without user ownership check (for internal use)

        Args:
            db: Database session
            resume_id: Resume ID

        Returns:
            Resume object or None if not found
        """
        return db.query(Resume).filter(Resume.id == resume_id).first()
