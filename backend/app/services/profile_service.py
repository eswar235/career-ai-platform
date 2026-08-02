"""
Profile service for handling user profile management
"""

import logging
import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.profile import (
    UserProfile,
    ProfileSkill,
    ProfileExperience,
    ProfileEducation,
    ProfileProject,
    ProfileCertification,
    ProfileVersion,
    ProfileCompletionTracking,
)
from app.schemas.profile import (
    UserProfileCreate,
    UserProfileUpdate,
    SkillCreate,
    SkillUpdate,
    ExperienceCreate,
    ExperienceUpdate,
    EducationCreate,
    EducationUpdate,
    ProjectCreate,
    ProjectUpdate,
    CertificationCreate,
    CertificationUpdate,
)

logger = logging.getLogger(__name__)


class ProfileService:
    """Service for managing user profiles"""

    @staticmethod
    def create_or_get_profile(
        db: Session,
        user_id: uuid.UUID,
        resume_id: uuid.UUID | None = None,
    ) -> UserProfile:
        """Create or get existing profile for a user"""
        existing = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        if existing:
            return existing

        profile = UserProfile(
            user_id=user_id,
            created_from_resume_id=resume_id,
            completion_percentage=0,
            verified_by_user=False,
        )

        # Create completion tracking record
        completion_tracking = ProfileCompletionTracking(profile=profile)
        db.add(profile)
        db.add(completion_tracking)
        db.commit()
        db.refresh(profile)

        # Create initial version
        ProfileService._create_version(db, profile.id, "Profile created")

        logger.info(f"Profile created for user {user_id}")
        return profile

    @staticmethod
    def get_profile(db: Session, user_id: uuid.UUID) -> UserProfile | None:
        """Get user profile"""
        return db.query(UserProfile).filter(UserProfile.user_id == user_id).first()

    @staticmethod
    def get_profile_by_id(db: Session, profile_id: uuid.UUID) -> UserProfile | None:
        """Get profile by ID"""
        return db.query(UserProfile).filter(UserProfile.id == profile_id).first()

    @staticmethod
    def update_profile(
        db: Session,
        profile_id: uuid.UUID,
        data: UserProfileUpdate,
    ) -> UserProfile:
        """Update profile information"""
        profile = db.query(UserProfile).filter(UserProfile.id == profile_id).first()
        if not profile:
            raise ValueError("Profile not found")

        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return profile

        for field, value in update_data.items():
            setattr(profile, field, value)

        profile.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(profile)

        # Create version for the change
        ProfileService._create_version(db, profile_id, "Profile updated")
        ProfileService._update_completion_percentage(db, profile_id)

        logger.info(f"Profile {profile_id} updated")
        return profile

    @staticmethod
    def _create_version(
        db: Session,
        profile_id: uuid.UUID,
        change_reason: str,
    ) -> ProfileVersion:
        """Create a version snapshot of the profile"""
        profile = db.query(UserProfile).filter(UserProfile.id == profile_id).first()
        if not profile:
            raise ValueError("Profile not found")

        # Get latest version number
        latest_version = (
            db.query(ProfileVersion)
            .filter(ProfileVersion.profile_id == profile_id)
            .order_by(ProfileVersion.version_number.desc())
            .first()
        )
        version_number = (latest_version.version_number + 1) if latest_version else 1

        # Create snapshot data
        snapshot_data = {
            "first_name": profile.first_name,
            "last_name": profile.last_name,
            "email": profile.email,
            "phone": profile.phone,
            "location": profile.location,
            "headline": profile.headline,
            "professional_summary": profile.professional_summary,
            "profile_picture_url": profile.profile_picture_url,
        }

        version = ProfileVersion(
            profile_id=profile_id,
            version_number=version_number,
            data=snapshot_data,
            change_reason=change_reason,
        )

        db.add(version)
        db.commit()
        db.refresh(version)

        return version

    @staticmethod
    def _update_completion_percentage(db: Session, profile_id: uuid.UUID) -> int:
        """Calculate and update profile completion percentage"""
        profile = db.query(UserProfile).filter(UserProfile.id == profile_id).first()
        if not profile:
            raise ValueError("Profile not found")

        tracking = (
            db.query(ProfileCompletionTracking)
            .filter(ProfileCompletionTracking.profile_id == profile_id)
            .first()
        )
        if not tracking:
            raise ValueError("Completion tracking not found")

        # Calculate completion
        percentage = 0
        total_sections = 8

        if profile.first_name and profile.last_name:
            percentage += 1
            tracking.personal_info_complete = True

        skill_count = db.query(ProfileSkill).filter(ProfileSkill.profile_id == profile_id).count()
        if skill_count > 0:
            percentage += 1
            tracking.skills_added = True

        experience_count = (
            db.query(ProfileExperience).filter(ProfileExperience.profile_id == profile_id).count()
        )
        if experience_count > 0:
            percentage += 1
            tracking.experience_added = True

        education_count = (
            db.query(ProfileEducation).filter(ProfileEducation.profile_id == profile_id).count()
        )
        if education_count > 0:
            percentage += 1
            tracking.education_added = True

        project_count = (
            db.query(ProfileProject).filter(ProfileProject.profile_id == profile_id).count()
        )
        if project_count > 0:
            percentage += 1
            tracking.projects_added = True

        cert_count = (
            db.query(ProfileCertification)
            .filter(ProfileCertification.profile_id == profile_id)
            .count()
        )
        if cert_count > 0:
            percentage += 1
            tracking.certifications_added = True

        if profile.profile_picture_url:
            percentage += 1
            tracking.profile_picture_added = True

        if profile.professional_summary:
            percentage += 1
            tracking.professional_summary_added = True

        profile.completion_percentage = int((percentage / total_sections) * 100)
        tracking.last_updated = datetime.now(timezone.utc)

        db.commit()
        db.refresh(profile)

        return profile.completion_percentage


class SkillService:
    """Service for managing profile skills"""

    @staticmethod
    def add_skill(db: Session, profile_id: uuid.UUID, data: SkillCreate) -> ProfileSkill:
        """Add a skill to profile"""
        profile = db.query(UserProfile).filter(UserProfile.id == profile_id).first()
        if not profile:
            raise ValueError("Profile not found")

        # Check for duplicate (case-insensitive)
        existing = (
            db.query(ProfileSkill)
            .filter(
                and_(
                    ProfileSkill.profile_id == profile_id,
                    ProfileSkill.skill_name.ilike(data.skill_name),
                )
            )
            .first()
        )
        if existing:
            raise ValueError(f"Skill '{data.skill_name}' already exists")

        skill = ProfileSkill(
            profile_id=profile_id,
            skill_name=data.skill_name,
            proficiency_level=data.proficiency_level,
            years_of_experience=data.years_of_experience,
        )

        db.add(skill)
        db.commit()
        db.refresh(skill)

        ProfileService._update_completion_percentage(db, profile_id)
        logger.info(f"Skill added to profile {profile_id}: {data.skill_name}")
        return skill

    @staticmethod
    def get_skills(db: Session, profile_id: uuid.UUID) -> list[ProfileSkill]:
        """Get all skills for a profile"""
        return (
            db.query(ProfileSkill)
            .filter(ProfileSkill.profile_id == profile_id)
            .order_by(ProfileSkill.created_at.desc())
            .all()
        )

    @staticmethod
    def update_skill(
        db: Session, skill_id: uuid.UUID, profile_id: uuid.UUID, data: SkillUpdate
    ) -> ProfileSkill:
        """Update a skill"""
        skill = (
            db.query(ProfileSkill)
            .filter(and_(ProfileSkill.id == skill_id, ProfileSkill.profile_id == profile_id))
            .first()
        )
        if not skill:
            raise ValueError("Skill not found")

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(skill, field, value)

        skill.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(skill)

        logger.info(f"Skill {skill_id} updated")
        return skill

    @staticmethod
    def delete_skill(db: Session, skill_id: uuid.UUID, profile_id: uuid.UUID) -> bool:
        """Delete a skill"""
        skill = (
            db.query(ProfileSkill)
            .filter(and_(ProfileSkill.id == skill_id, ProfileSkill.profile_id == profile_id))
            .first()
        )
        if not skill:
            raise ValueError("Skill not found")

        db.delete(skill)
        db.commit()

        ProfileService._update_completion_percentage(db, profile_id)
        logger.info(f"Skill {skill_id} deleted")
        return True


class ExperienceService:
    """Service for managing work experience"""

    @staticmethod
    def add_experience(
        db: Session, profile_id: uuid.UUID, data: ExperienceCreate
    ) -> ProfileExperience:
        """Add work experience to profile"""
        profile = db.query(UserProfile).filter(UserProfile.id == profile_id).first()
        if not profile:
            raise ValueError("Profile not found")

        experience = ProfileExperience(
            profile_id=profile_id,
            job_title=data.job_title,
            company_name=data.company_name,
            company_industry=data.company_industry,
            employment_type=data.employment_type,
            location=data.location,
            description=data.description,
            start_date=data.start_date,
            end_date=data.end_date,
            currently_working=data.currently_working,
        )

        db.add(experience)
        db.commit()
        db.refresh(experience)

        ProfileService._update_completion_percentage(db, profile_id)
        logger.info(f"Experience added to profile {profile_id}: {data.job_title}")
        return experience

    @staticmethod
    def get_experiences(db: Session, profile_id: uuid.UUID) -> list[ProfileExperience]:
        """Get all experiences for a profile"""
        return (
            db.query(ProfileExperience)
            .filter(ProfileExperience.profile_id == profile_id)
            .order_by(ProfileExperience.start_date.desc())
            .all()
        )

    @staticmethod
    def update_experience(
        db: Session,
        experience_id: uuid.UUID,
        profile_id: uuid.UUID,
        data: ExperienceUpdate,
    ) -> ProfileExperience:
        """Update work experience"""
        experience = (
            db.query(ProfileExperience)
            .filter(
                and_(ProfileExperience.id == experience_id, ProfileExperience.profile_id == profile_id)
            )
            .first()
        )
        if not experience:
            raise ValueError("Experience not found")

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(experience, field, value)

        experience.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(experience)

        logger.info(f"Experience {experience_id} updated")
        return experience

    @staticmethod
    def delete_experience(db: Session, experience_id: uuid.UUID, profile_id: uuid.UUID) -> bool:
        """Delete work experience"""
        experience = (
            db.query(ProfileExperience)
            .filter(
                and_(ProfileExperience.id == experience_id, ProfileExperience.profile_id == profile_id)
            )
            .first()
        )
        if not experience:
            raise ValueError("Experience not found")

        db.delete(experience)
        db.commit()

        ProfileService._update_completion_percentage(db, profile_id)
        logger.info(f"Experience {experience_id} deleted")
        return True


class EducationService:
    """Service for managing education"""

    @staticmethod
    def add_education(
        db: Session, profile_id: uuid.UUID, data: EducationCreate
    ) -> ProfileEducation:
        """Add education to profile"""
        profile = db.query(UserProfile).filter(UserProfile.id == profile_id).first()
        if not profile:
            raise ValueError("Profile not found")

        education = ProfileEducation(
            profile_id=profile_id,
            institution_name=data.institution_name,
            degree=data.degree,
            field_of_study=data.field_of_study,
            start_date=data.start_date,
            end_date=data.end_date,
            description=data.description,
            grade=data.grade,
            activities_societies=data.activities_societies,
        )

        db.add(education)
        db.commit()
        db.refresh(education)

        ProfileService._update_completion_percentage(db, profile_id)
        logger.info(f"Education added to profile {profile_id}: {data.institution_name}")
        return education

    @staticmethod
    def get_education(db: Session, profile_id: uuid.UUID) -> list[ProfileEducation]:
        """Get all education for a profile"""
        return (
            db.query(ProfileEducation)
            .filter(ProfileEducation.profile_id == profile_id)
            .order_by(ProfileEducation.start_date.desc())
            .all()
        )

    @staticmethod
    def update_education(
        db: Session, education_id: uuid.UUID, profile_id: uuid.UUID, data: EducationUpdate
    ) -> ProfileEducation:
        """Update education"""
        education = (
            db.query(ProfileEducation)
            .filter(
                and_(ProfileEducation.id == education_id, ProfileEducation.profile_id == profile_id)
            )
            .first()
        )
        if not education:
            raise ValueError("Education not found")

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(education, field, value)

        education.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(education)

        logger.info(f"Education {education_id} updated")
        return education

    @staticmethod
    def delete_education(db: Session, education_id: uuid.UUID, profile_id: uuid.UUID) -> bool:
        """Delete education"""
        education = (
            db.query(ProfileEducation)
            .filter(
                and_(ProfileEducation.id == education_id, ProfileEducation.profile_id == profile_id)
            )
            .first()
        )
        if not education:
            raise ValueError("Education not found")

        db.delete(education)
        db.commit()

        ProfileService._update_completion_percentage(db, profile_id)
        logger.info(f"Education {education_id} deleted")
        return True


class ProjectService:
    """Service for managing portfolio projects"""

    @staticmethod
    def add_project(db: Session, profile_id: uuid.UUID, data: ProjectCreate) -> ProfileProject:
        """Add project to profile"""
        profile = db.query(UserProfile).filter(UserProfile.id == profile_id).first()
        if not profile:
            raise ValueError("Profile not found")

        project = ProfileProject(
            profile_id=profile_id,
            project_name=data.project_name,
            description=data.description,
            skills_used=data.skills_used,
            start_date=data.start_date,
            end_date=data.end_date,
            project_url=data.project_url,
            image_url=data.image_url,
        )

        db.add(project)
        db.commit()
        db.refresh(project)

        ProfileService._update_completion_percentage(db, profile_id)
        logger.info(f"Project added to profile {profile_id}: {data.project_name}")
        return project

    @staticmethod
    def get_projects(db: Session, profile_id: uuid.UUID) -> list[ProfileProject]:
        """Get all projects for a profile"""
        return (
            db.query(ProfileProject)
            .filter(ProfileProject.profile_id == profile_id)
            .order_by(ProfileProject.start_date.desc())
            .all()
        )

    @staticmethod
    def update_project(
        db: Session, project_id: uuid.UUID, profile_id: uuid.UUID, data: ProjectUpdate
    ) -> ProfileProject:
        """Update project"""
        project = (
            db.query(ProfileProject)
            .filter(and_(ProfileProject.id == project_id, ProfileProject.profile_id == profile_id))
            .first()
        )
        if not project:
            raise ValueError("Project not found")

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(project, field, value)

        project.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(project)

        logger.info(f"Project {project_id} updated")
        return project

    @staticmethod
    def delete_project(db: Session, project_id: uuid.UUID, profile_id: uuid.UUID) -> bool:
        """Delete project"""
        project = (
            db.query(ProfileProject)
            .filter(and_(ProfileProject.id == project_id, ProfileProject.profile_id == profile_id))
            .first()
        )
        if not project:
            raise ValueError("Project not found")

        db.delete(project)
        db.commit()

        ProfileService._update_completion_percentage(db, profile_id)
        logger.info(f"Project {project_id} deleted")
        return True


class CertificationService:
    """Service for managing certifications"""

    @staticmethod
    def add_certification(
        db: Session, profile_id: uuid.UUID, data: CertificationCreate
    ) -> ProfileCertification:
        """Add certification to profile"""
        profile = db.query(UserProfile).filter(UserProfile.id == profile_id).first()
        if not profile:
            raise ValueError("Profile not found")

        certification = ProfileCertification(
            profile_id=profile_id,
            certification_name=data.certification_name,
            issuing_organization=data.issuing_organization,
            issue_date=data.issue_date,
            expiration_date=data.expiration_date,
            credential_id=data.credential_id,
            credential_url=data.credential_url,
        )

        db.add(certification)
        db.commit()
        db.refresh(certification)

        ProfileService._update_completion_percentage(db, profile_id)
        logger.info(f"Certification added to profile {profile_id}: {data.certification_name}")
        return certification

    @staticmethod
    def get_certifications(db: Session, profile_id: uuid.UUID) -> list[ProfileCertification]:
        """Get all certifications for a profile"""
        return (
            db.query(ProfileCertification)
            .filter(ProfileCertification.profile_id == profile_id)
            .order_by(ProfileCertification.issue_date.desc())
            .all()
        )

    @staticmethod
    def update_certification(
        db: Session,
        certification_id: uuid.UUID,
        profile_id: uuid.UUID,
        data: CertificationUpdate,
    ) -> ProfileCertification:
        """Update certification"""
        certification = (
            db.query(ProfileCertification)
            .filter(
                and_(
                    ProfileCertification.id == certification_id,
                    ProfileCertification.profile_id == profile_id,
                )
            )
            .first()
        )
        if not certification:
            raise ValueError("Certification not found")

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(certification, field, value)

        certification.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(certification)

        logger.info(f"Certification {certification_id} updated")
        return certification

    @staticmethod
    def delete_certification(
        db: Session, certification_id: uuid.UUID, profile_id: uuid.UUID
    ) -> bool:
        """Delete certification"""
        certification = (
            db.query(ProfileCertification)
            .filter(
                and_(
                    ProfileCertification.id == certification_id,
                    ProfileCertification.profile_id == profile_id,
                )
            )
            .first()
        )
        if not certification:
            raise ValueError("Certification not found")

        db.delete(certification)
        db.commit()

        ProfileService._update_completion_percentage(db, profile_id)
        logger.info(f"Certification {certification_id} deleted")
        return True
