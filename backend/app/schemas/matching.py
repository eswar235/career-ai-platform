"""
Pydantic schemas for job matching and embeddings
"""

from datetime import datetime
from typing import Optional
import uuid

from pydantic import BaseModel, Field


# Embedding Schemas
class ResumeEmbeddingResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    content: str
    skills_extracted: Optional[list[str]]
    experience_summary: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class JobEmbeddingResponse(BaseModel):
    id: uuid.UUID
    job_id: uuid.UUID
    content: str
    skills_required_normalized: Optional[list[str]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Job Match Schemas
class JobMatchResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    job_id: uuid.UUID
    match_percentage: int = Field(..., ge=0, le=100)
    match_score: float = Field(..., ge=0.0, le=1.0)
    skills_match: Optional[int]
    skills_missing: Optional[int]
    strengths: Optional[list[str]]
    gaps: Optional[list[str]]
    recommendations: Optional[list[str]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class JobMatchDetailResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    job_id: uuid.UUID
    match_percentage: int
    match_score: float
    skills_match: Optional[int]
    skills_missing: Optional[int]
    strengths: Optional[list[str]]
    gaps: Optional[list[str]]
    recommendations: Optional[list[str]]
    job: Optional[dict] = None  # Job details
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Skill Analysis Schemas
class SkillAnalysis(BaseModel):
    user_skills: list[str] = Field(..., description="Skills from user profile")
    job_required_skills: list[str] = Field(..., description="Skills required for job")
    matched_skills: list[str] = Field(..., description="Skills that match")
    missing_skills: list[str] = Field(..., description="Skills user doesn't have")
    match_count: int
    missing_count: int
    skill_match_percentage: float = Field(..., ge=0.0, le=100.0)


# Matching Request/Response
class MatchingRequest(BaseModel):
    job_id: uuid.UUID = Field(..., description="Job ID to match against")


class MatchingResponse(BaseModel):
    user_id: uuid.UUID
    job_id: uuid.UUID
    match_percentage: int
    match_score: float
    skill_analysis: SkillAnalysis
    strengths: list[str]
    gaps: list[str]
    recommendations: list[str]


class BulkMatchingResponse(BaseModel):
    total_matches: int
    matched_jobs: int
    high_matches: int  # > 75%
    moderate_matches: int  # 50-75%
    low_matches: int  # < 50%
    timestamp: datetime


# User Matches List
class UserMatchesList(BaseModel):
    total: int
    skip: int
    limit: int
    matches: list[JobMatchResponse]

    class Config:
        from_attributes = True
