"""
Pydantic schemas for resume-related requests and responses
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ResumeBase(BaseModel):
    """Base resume schema"""

    filename: str = Field(..., description="Filename")
    original_filename: str = Field(..., description="Original filename as uploaded")
    file_size: int = Field(..., gt=0, description="File size in bytes")
    mime_type: str = Field(default="application/pdf", description="MIME type")
    version: Optional[str] = Field(None, description="Resume version/label")


class ResumeCreate(BaseModel):
    """Schema for creating a resume (used internally after file validation)"""

    filename: str = Field(..., description="Stored filename")
    original_filename: str = Field(..., description="Original filename")
    file_size: int = Field(..., gt=0, description="File size in bytes")
    storage_path: str = Field(..., description="Storage path")
    mime_type: str = Field(default="application/pdf", description="MIME type")
    version: Optional[str] = Field(None, description="Resume version/label")


class ResumeResponse(ResumeBase):
    """Schema for resume response"""

    id: UUID = Field(..., description="Resume ID")
    user_id: UUID = Field(..., description="User ID")
    storage_path: str = Field(..., description="Storage path")
    parsing_status: str = Field(..., description="Parsing status")
    parsing_error: Optional[str] = Field(None, description="Parsing error message")
    is_active: bool = Field(..., description="Is this the active resume")
    uploaded_at: datetime = Field(..., description="Upload timestamp")
    parsed_at: Optional[datetime] = Field(None, description="Parse completion timestamp")
    updated_at: datetime = Field(..., description="Update timestamp")

    class Config:
        from_attributes = True


class ResumeListResponse(BaseModel):
    """Schema for listing resumes"""

    resumes: list[ResumeResponse] = Field(..., description="List of resumes")
    total: int = Field(..., description="Total number of resumes")


class ResumeUploadResponse(BaseModel):
    """Schema for upload response"""

    id: UUID = Field(..., description="Resume ID")
    filename: str = Field(..., description="Filename")
    original_filename: str = Field(..., description="Original filename")
    file_size: int = Field(..., description="File size in bytes")
    uploaded_at: datetime = Field(..., description="Upload timestamp")
    message: str = Field(default="Resume uploaded successfully", description="Success message")

    class Config:
        from_attributes = True


class ResumeSetActiveRequest(BaseModel):
    """Schema for setting a resume as active"""

    resume_id: UUID = Field(..., description="Resume ID to set as active")


class ResumeSoftDeleteRequest(BaseModel):
    """Schema for deleting a resume"""

    resume_id: UUID = Field(..., description="Resume ID to delete")
