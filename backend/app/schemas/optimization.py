"""
Pydantic schemas for resume optimization
"""

from datetime import datetime
from typing import Optional
import uuid

from pydantic import BaseModel, Field


# Optimization Suggestion Schemas
class OptimizationSuggestionResponse(BaseModel):
    id: uuid.UUID
    optimization_id: uuid.UUID
    category: str
    suggestion: str
    priority: str
    impact_score: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


# Resume Optimization Schemas
class ResumeOptimizationCreate(BaseModel):
    original_content: str = Field(..., description="Original resume content")


class ResumeOptimizationResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    original_content: str
    optimized_content: Optional[str]
    ats_score: Optional[int] = Field(None, ge=0, le=100)
    keyword_score: Optional[int] = Field(None, ge=0, le=100)
    formatting_score: Optional[int] = Field(None, ge=0, le=100)
    readability_score: Optional[int] = Field(None, ge=0, le=100)
    overall_score: Optional[int] = Field(None, ge=0, le=100)
    created_at: datetime
    updated_at: datetime
    suggestions: list[OptimizationSuggestionResponse] = []

    class Config:
        from_attributes = True


class ResumeOptimizationDetailResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    ats_score: Optional[int]
    keyword_score: Optional[int]
    formatting_score: Optional[int]
    readability_score: Optional[int]
    overall_score: Optional[int]
    suggestions: list[OptimizationSuggestionResponse]
    optimized_content: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Tailored Resume Schemas
class TailoredResumeCreate(BaseModel):
    job_id: uuid.UUID


class TailoredResumeResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    job_id: uuid.UUID
    tailored_content: str
    match_keywords: Optional[int]
    ats_score: Optional[int] = Field(None, ge=0, le=100)
    keyword_score: Optional[int] = Field(None, ge=0, le=100)
    recommendations: Optional[list[str]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Optimization Score Breakdown
class OptimizationScoreBreakdown(BaseModel):
    ats_score: int = Field(..., ge=0, le=100, description="ATS compatibility score")
    keyword_score: int = Field(..., ge=0, le=100, description="Keyword match score")
    formatting_score: int = Field(..., ge=0, le=100, description="Formatting quality score")
    readability_score: int = Field(..., ge=0, le=100, description="Readability score")
    overall_score: int = Field(..., ge=0, le=100, description="Overall optimization score")


# Keyword Analysis
class KeywordAnalysis(BaseModel):
    job_keywords: list[str]
    resume_keywords: list[str]
    matched_keywords: list[str]
    missing_keywords: list[str]
    keyword_density: dict[str, float]
    match_percentage: float = Field(..., ge=0.0, le=100.0)


# Download Response
class DownloadResponse(BaseModel):
    download_url: str
    filename: str
    content_type: str
    file_size: int
    created_at: datetime
