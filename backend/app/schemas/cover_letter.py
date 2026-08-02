"""
Pydantic schemas for cover letter generation
"""

from datetime import datetime
from typing import Optional
import uuid

from pydantic import BaseModel, Field


# Cover Letter Base Schema
class CoverLetterBase(BaseModel):
    """Base cover letter schema"""

    content: str = Field(..., description="Cover letter content")
    is_draft: bool = Field(default=True, description="Is this a draft?")
    custom_edits: Optional[str] = Field(None, description="Custom edits to the cover letter")


# Cover Letter Create Schema
class CoverLetterCreate(BaseModel):
    """Create cover letter request"""

    job_id: uuid.UUID = Field(..., description="Job ID to generate cover letter for")
    template_id: Optional[uuid.UUID] = Field(None, description="Optional template ID to use")


# Cover Letter Update Schema
class CoverLetterUpdate(BaseModel):
    """Update cover letter request"""

    content: Optional[str] = Field(None, description="Updated cover letter content")
    is_draft: Optional[bool] = Field(None, description="Update draft status")
    custom_edits: Optional[str] = Field(None, description="Custom edits")


# Cover Letter Response Schema
class CoverLetterResponse(BaseModel):
    """Cover letter response"""

    id: uuid.UUID
    user_id: uuid.UUID
    job_id: uuid.UUID
    content: str
    version_number: int
    is_draft: bool
    custom_edits: Optional[str]
    ai_model: Optional[str]
    generated_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Cover Letter Detail Response
class CoverLetterDetailResponse(CoverLetterResponse):
    """Detailed cover letter with exports"""

    exports: list["LetterExportResponse"] = Field(default_factory=list)

    class Config:
        from_attributes = True


# Letter Template Base Schema
class LetterTemplateBase(BaseModel):
    """Base letter template schema"""

    name: str = Field(..., min_length=1, max_length=255, description="Template name")
    content: str = Field(..., description="Template content")
    is_default: bool = Field(default=False, description="Is this the default template?")


# Letter Template Create Schema
class LetterTemplateCreate(LetterTemplateBase):
    """Create letter template request"""

    pass


# Letter Template Update Schema
class LetterTemplateUpdate(BaseModel):
    """Update letter template request"""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = Field(None)
    is_default: Optional[bool] = Field(None)


# Letter Template Response Schema
class LetterTemplateResponse(BaseModel):
    """Letter template response"""

    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    content: str
    is_default: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Letter Export Base Schema
class LetterExportBase(BaseModel):
    """Base letter export schema"""

    format: str = Field(..., description="Export format (pdf, docx, txt)")


# Letter Export Create Schema
class LetterExportCreate(LetterExportBase):
    """Create letter export request"""

    pass


# Letter Export Response Schema
class LetterExportResponse(BaseModel):
    """Letter export response"""

    id: uuid.UUID
    cover_letter_id: uuid.UUID
    format: str
    file_url: Optional[str]
    file_size: Optional[int]
    exported_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# Generation Request
class GenerateCoverLetterRequest(BaseModel):
    """Request to generate a cover letter"""

    job_id: uuid.UUID = Field(..., description="Job ID to generate letter for")
    template_id: Optional[uuid.UUID] = Field(None, description="Optional template to use as base")
    use_profile: bool = Field(default=True, description="Use user profile data in generation")


# Generation Response
class GenerateCoverLetterResponse(BaseModel):
    """Response from cover letter generation"""

    id: uuid.UUID
    content: str
    version_number: int
    generated_at: datetime

    class Config:
        from_attributes = True


# Batch Generation Request
class BatchGenerateCoverLettersRequest(BaseModel):
    """Request to generate multiple cover letters"""

    job_ids: list[uuid.UUID] = Field(..., description="List of job IDs")
    template_id: Optional[uuid.UUID] = Field(None, description="Optional template to use")


# Batch Generation Response
class BatchGenerateCoverLettersResponse(BaseModel):
    """Response from batch generation"""

    generated: int = Field(..., description="Number of letters generated")
    job_ids: list[uuid.UUID]
    timestamp: datetime


# Publication Request
class PublishCoverLetterRequest(BaseModel):
    """Request to publish/finalize a cover letter"""

    version_id: uuid.UUID = Field(..., description="Cover letter ID to publish")


# Publication Response
class PublishCoverLetterResponse(BaseModel):
    """Response from publishing a cover letter"""

    id: uuid.UUID
    is_draft: bool
    published_at: datetime

    class Config:
        from_attributes = True
