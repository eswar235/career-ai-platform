"""
Profile API routes for user profile management
"""

import logging
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.profile import (
    UserProfileCreate,
    UserProfileUpdate,
    UserProfileResponse,
    UserProfileDetailResponse,
    SkillCreate,
    SkillResponse,
    SkillUpdate,
    ExperienceCreate,
    ExperienceResponse,
    ExperienceUpdate,
    EducationCreate,
    EducationResponse,
    EducationUpdate,
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
    CertificationCreate,
    CertificationResponse,
    CertificationUpdate,
)
from app.services.profile_service import (
    ProfileService,
    SkillService,
    ExperienceService,
    EducationService,
    ProjectService,
    CertificationService,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/profile", tags=["profile"])


# Profile endpoints
@router.post("/", response_model=UserProfileResponse)
def create_or_get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create or get user profile"""
    profile = ProfileService.create_or_get_profile(db, current_user.id)
    return profile


@router.get("/", response_model=UserProfileResponse)
def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get current user profile"""
    profile = ProfileService.get_profile(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return profile


@router.patch("/", response_model=UserProfileResponse)
def update_profile(
    data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update user profile"""
    profile = ProfileService.get_profile(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    try:
        updated_profile = ProfileService.update_profile(db, profile.id, data)
        return updated_profile
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# Skills endpoints
@router.post("/skills", response_model=SkillResponse)
def add_skill(
    data: SkillCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add skill to profile"""
    profile = ProfileService.get_profile(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    try:
        skill = SkillService.add_skill(db, profile.id, data)
        return skill
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/skills", response_model=list[SkillResponse])
def get_skills(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all skills for user profile"""
    profile = ProfileService.get_profile(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    skills = SkillService.get_skills(db, profile.id)
    return skills


@router.patch("/skills/{skill_id}", response_model=SkillResponse)
def update_skill(
    skill_id: uuid.UUID,
    data: SkillUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update skill"""
    profile = ProfileService.get_profile(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    try:
        skill = SkillService.update_skill(db, skill_id, profile.id, data)
        return skill
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/skills/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_skill(
    skill_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete skill"""
    profile = ProfileService.get_profile(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    try:
        SkillService.delete_skill(db, skill_id, profile.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# Experience endpoints
@router.post("/experiences", response_model=ExperienceResponse)
def add_experience(
    data: ExperienceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add work experience to profile"""
    profile = ProfileService.get_profile(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    try:
        experience = ExperienceService.add_experience(db, profile.id, data)
        return experience
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/experiences", response_model=list[ExperienceResponse])
def get_experiences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all experiences for user profile"""
    profile = ProfileService.get_profile(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    experiences = ExperienceService.get_experiences(db, profile.id)
    return experiences


@router.patch("/experiences/{experience_id}", response_model=ExperienceResponse)
def update_experience(
    experience_id: uuid.UUID,
    data: ExperienceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update work experience"""
    profile = ProfileService.get_profile(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    try:
        experience = ExperienceService.update_experience(db, experience_id, profile.id, data)
        return experience
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/experiences/{experience_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_experience(
    experience_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete work experience"""
    profile = ProfileService.get_profile(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    try:
        ExperienceService.delete_experience(db, experience_id, profile.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# Education endpoints
@router.post("/education", response_model=EducationResponse)
def add_education(
    data: EducationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add education to profile"""
    profile = ProfileService.get_profile(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    try:
        education = EducationService.add_education(db, profile.id, data)
        return education
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/education", response_model=list[EducationResponse])
def get_education(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all education for user profile"""
    profile = ProfileService.get_profile(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    education = EducationService.get_education(db, profile.id)
    return education


@router.patch("/education/{education_id}", response_model=EducationResponse)
def update_education(
    education_id: uuid.UUID,
    data: EducationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update education"""
    profile = ProfileService.get_profile(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    try:
        education = EducationService.update_education(db, education_id, profile.id, data)
        return education
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/education/{education_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_education(
    education_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete education"""
    profile = ProfileService.get_profile(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    try:
        EducationService.delete_education(db, education_id, profile.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# Projects endpoints
@router.post("/projects", response_model=ProjectResponse)
def add_project(
    data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add project to profile"""
    profile = ProfileService.get_profile(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    try:
        project = ProjectService.add_project(db, profile.id, data)
        return project
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/projects", response_model=list[ProjectResponse])
def get_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all projects for user profile"""
    profile = ProfileService.get_profile(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    projects = ProjectService.get_projects(db, profile.id)
    return projects


@router.patch("/projects/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: uuid.UUID,
    data: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update project"""
    profile = ProfileService.get_profile(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    try:
        project = ProjectService.update_project(db, project_id, profile.id, data)
        return project
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete project"""
    profile = ProfileService.get_profile(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    try:
        ProjectService.delete_project(db, project_id, profile.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# Certifications endpoints
@router.post("/certifications", response_model=CertificationResponse)
def add_certification(
    data: CertificationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add certification to profile"""
    profile = ProfileService.get_profile(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    try:
        certification = CertificationService.add_certification(db, profile.id, data)
        return certification
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/certifications", response_model=list[CertificationResponse])
def get_certifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all certifications for user profile"""
    profile = ProfileService.get_profile(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    certifications = CertificationService.get_certifications(db, profile.id)
    return certifications


@router.patch("/certifications/{certification_id}", response_model=CertificationResponse)
def update_certification(
    certification_id: uuid.UUID,
    data: CertificationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update certification"""
    profile = ProfileService.get_profile(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    try:
        certification = CertificationService.update_certification(
            db, certification_id, profile.id, data
        )
        return certification
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/certifications/{certification_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_certification(
    certification_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete certification"""
    profile = ProfileService.get_profile(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    try:
        CertificationService.delete_certification(db, certification_id, profile.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
