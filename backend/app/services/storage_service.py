"""
Storage service for handling file uploads and storage
Supports both local storage (development) and Supabase (production)
"""

import logging
import os
import uuid
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class StorageService:
    """Service for handling file storage operations"""

    # Storage configuration
    STORAGE_DIR = Path("uploads/resumes")
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB (per spec requirement)
    ALLOWED_EXTENSIONS = {".pdf"}
    ALLOWED_MIME_TYPES = {"application/pdf"}

    @staticmethod
    def validate_file(
        filename: str,
        file_size: int,
        mime_type: str,
    ) -> tuple[bool, str]:
        """
        Validate uploaded file

        Args:
            filename: Original filename
            file_size: File size in bytes
            mime_type: MIME type

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check file extension
        file_ext = Path(filename).suffix.lower()
        if file_ext not in StorageService.ALLOWED_EXTENSIONS:
            return (
                False,
                f"Invalid file type. Only PDF files are allowed. Got: {file_ext}",
            )

        # Check MIME type
        if mime_type not in StorageService.ALLOWED_MIME_TYPES:
            return (
                False,
                f"Invalid MIME type. Expected application/pdf, got: {mime_type}",
            )

        # Check file size
        if file_size > StorageService.MAX_FILE_SIZE:
            max_mb = StorageService.MAX_FILE_SIZE / (1024 * 1024)
            return (
                False,
                f"File too large. Maximum size is {max_mb}MB, got {file_size / (1024 * 1024):.2f}MB",
            )

        # Check if filename is not empty
        if not filename or len(filename.strip()) == 0:
            return False, "Filename cannot be empty"

        return True, ""

    @staticmethod
    def generate_storage_filename(
        user_id: uuid.UUID,
        original_filename: str,
    ) -> str:
        """
        Generate a unique storage filename to prevent collisions and maintain security

        Args:
            user_id: User ID
            original_filename: Original filename

        Returns:
            Generated filename
        """
        # Get file extension
        file_ext = Path(original_filename).suffix.lower()

        # Create unique filename with user_id and timestamp
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        unique_id = uuid.uuid4().hex[:8]

        return f"{user_id}/{timestamp}_{unique_id}{file_ext}"

    @staticmethod
    def save_file_local(
        file_content: bytes,
        storage_path: str,
    ) -> bool:
        """
        Save file to local storage (development)

        Args:
            file_content: File content as bytes
            storage_path: Path where file should be stored

        Returns:
            True if successful, False otherwise
        """
        try:
            # Create directory if it doesn't exist
            full_path = StorageService.STORAGE_DIR / storage_path
            full_path.parent.mkdir(parents=True, exist_ok=True)

            # Write file
            with open(full_path, "wb") as f:
                f.write(file_content)

            logger.info(f"File saved successfully: {storage_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to save file {storage_path}: {str(e)}")
            return False

    @staticmethod
    def delete_file_local(storage_path: str) -> bool:
        """
        Delete file from local storage

        Args:
            storage_path: Path of file to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            full_path = StorageService.STORAGE_DIR / storage_path
            if full_path.exists():
                full_path.unlink()
                logger.info(f"File deleted successfully: {storage_path}")
                return True
            else:
                logger.warning(f"File not found: {storage_path}")
                return False

        except Exception as e:
            logger.error(f"Failed to delete file {storage_path}: {str(e)}")
            return False

    @staticmethod
    def get_file_local(storage_path: str) -> bytes | None:
        """
        Read file from local storage

        Args:
            storage_path: Path of file to read

        Returns:
            File content as bytes, or None if not found
        """
        try:
            full_path = StorageService.STORAGE_DIR / storage_path
            if full_path.exists():
                with open(full_path, "rb") as f:
                    return f.read()
            else:
                logger.warning(f"File not found: {storage_path}")
                return None

        except Exception as e:
            logger.error(f"Failed to read file {storage_path}: {str(e)}")
            return None
