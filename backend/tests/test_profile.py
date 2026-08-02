"""
Tests for profile service and endpoints
"""

import uuid
from datetime import date
import pytest
from sqlalchemy.orm import Session

from app.models.profile import UserProfile, ProfileSkill
from app.services.profile_service import (
    ProfileService,
    SkillService,
    ExperienceService,
    EducationService,
    ProjectService,
    CertificationService,
)
from app.schemas.profile import (
    SkillCreate,
    ExperienceCreate,
    EducationCreate,
    ProjectCreate,
    CertificationCreate,
    UserProfileUpdate,
)


class TestProfileService:
    """Tests for ProfileService"""

    def test_create_or_get_profile(self, db: Session, test_user_id: uuid.UUID):
        """Test creating a new profile"""
        profile = ProfileService.create_or_get_profile(db, test_user_id)
        assert profile is not None
        assert profile.user_id == test_user_id
        assert profile.completion_percentage == 0
        assert profile.verified_by_user is False

    def test_get_existing_profile(self, db: Session, test_user_id: uuid.UUID):
        """Test getting existing profile"""
        # Create profile first
        profile1 = ProfileService.create_or_get_profile(db, test_user_id)
        # Get it again
        profile2 = ProfileService.get_profile(db, test_user_id)
        assert profile1.id == profile2.id

    def test_update_profile(self, db: Session, test_user_id: uuid.UUID):
        """Test updating profile"""
        profile = ProfileService.create_or_get_profile(db, test_user_id)
        update_data = UserProfileUpdate(
            first_name="John",
            last_name="Doe",
            headline="Software Engineer",
        )
        updated = ProfileService.update_profile(db, profile.id, update_data)
        assert updated.first_name == "John"
        assert updated.last_name == "Doe"
        assert updated.headline == "Software Engineer"

    def test_completion_percentage(self, db: Session, test_user_id: uuid.UUID):
        """Test completion percentage calculation"""
        profile = ProfileService.create_or_get_profile(db, test_user_id)
        initial_percentage = profile.completion_percentage
        assert initial_percentage == 0

        # Add name
        update_data = UserProfileUpdate(first_name="John", last_name="Doe")
        ProfileService.update_profile(db, profile.id, update_data)
        profile = db.query(UserProfile).filter(UserProfile.id == profile.id).first()
        assert profile.completion_percentage > 0


class TestSkillService:
    """Tests for SkillService"""

    def test_add_skill(self, db: Session, test_user_id: uuid.UUID):
        """Test adding a skill"""
        profile = ProfileService.create_or_get_profile(db, test_user_id)
        skill_data = SkillCreate(
            skill_name="Python",
            proficiency_level="Advanced",
            years_of_experience=5,
        )
        skill = SkillService.add_skill(db, profile.id, skill_data)
        assert skill.skill_name == "Python"
        assert skill.proficiency_level == "Advanced"
        assert skill.years_of_experience == 5

    def test_duplicate_skill(self, db: Session, test_user_id: uuid.UUID):
        """Test adding duplicate skill"""
        profile = ProfileService.create_or_get_profile(db, test_user_id)
        skill_data = SkillCreate(skill_name="Python")
        SkillService.add_skill(db, profile.id, skill_data)

        # Try to add again
        with pytest.raises(ValueError):
            SkillService.add_skill(db, profile.id, skill_data)

    def test_get_skills(self, db: Session, test_user_id: uuid.UUID):
        """Test retrieving skills"""
        profile = ProfileService.create_or_get_profile(db, test_user_id)
        skill_data1 = SkillCreate(skill_name="Python")
        skill_data2 = SkillCreate(skill_name="JavaScript")

        SkillService.add_skill(db, profile.id, skill_data1)
        SkillService.add_skill(db, profile.id, skill_data2)

        skills = SkillService.get_skills(db, profile.id)
        assert len(skills) == 2

    def test_delete_skill(self, db: Session, test_user_id: uuid.UUID):
        """Test deleting a skill"""
        profile = ProfileService.create_or_get_profile(db, test_user_id)
        skill_data = SkillCreate(skill_name="Python")
        skill = SkillService.add_skill(db, profile.id, skill_data)

        SkillService.delete_skill(db, skill.id, profile.id)
        skills = SkillService.get_skills(db, profile.id)
        assert len(skills) == 0


class TestExperienceService:
    """Tests for ExperienceService"""

    def test_add_experience(self, db: Session, test_user_id: uuid.UUID):
        """Test adding work experience"""
        profile = ProfileService.create_or_get_profile(db, test_user_id)
        exp_data = ExperienceCreate(
            job_title="Software Engineer",
            company_name="Tech Corp",
            start_date=date(2020, 1, 1),
            currently_working=True,
        )
        experience = ExperienceService.add_experience(db, profile.id, exp_data)
        assert experience.job_title == "Software Engineer"
        assert experience.company_name == "Tech Corp"
        assert experience.currently_working is True

    def test_get_experiences(self, db: Session, test_user_id: uuid.UUID):
        """Test retrieving experiences"""
        profile = ProfileService.create_or_get_profile(db, test_user_id)
        exp_data1 = ExperienceCreate(
            job_title="Engineer", company_name="Corp1", start_date=date(2020, 1, 1)
        )
        exp_data2 = ExperienceCreate(
            job_title="Developer", company_name="Corp2", start_date=date(2022, 1, 1)
        )

        ExperienceService.add_experience(db, profile.id, exp_data1)
        ExperienceService.add_experience(db, profile.id, exp_data2)

        experiences = ExperienceService.get_experiences(db, profile.id)
        assert len(experiences) == 2


class TestEducationService:
    """Tests for EducationService"""

    def test_add_education(self, db: Session, test_user_id: uuid.UUID):
        """Test adding education"""
        profile = ProfileService.create_or_get_profile(db, test_user_id)
        edu_data = EducationCreate(
            institution_name="MIT",
            degree="Bachelor",
            field_of_study="Computer Science",
        )
        education = EducationService.add_education(db, profile.id, edu_data)
        assert education.institution_name == "MIT"
        assert education.degree == "Bachelor"

    def test_get_education(self, db: Session, test_user_id: uuid.UUID):
        """Test retrieving education"""
        profile = ProfileService.create_or_get_profile(db, test_user_id)
        edu_data = EducationCreate(institution_name="MIT")
        EducationService.add_education(db, profile.id, edu_data)

        education = EducationService.get_education(db, profile.id)
        assert len(education) == 1


class TestProjectService:
    """Tests for ProjectService"""

    def test_add_project(self, db: Session, test_user_id: uuid.UUID):
        """Test adding a project"""
        profile = ProfileService.create_or_get_profile(db, test_user_id)
        proj_data = ProjectCreate(
            project_name="AI Assistant",
            description="An AI-powered assistant",
            skills_used=["Python", "FastAPI"],
        )
        project = ProjectService.add_project(db, profile.id, proj_data)
        assert project.project_name == "AI Assistant"
        assert "Python" in project.skills_used

    def test_get_projects(self, db: Session, test_user_id: uuid.UUID):
        """Test retrieving projects"""
        profile = ProfileService.create_or_get_profile(db, test_user_id)
        proj_data = ProjectCreate(project_name="Project 1")
        ProjectService.add_project(db, profile.id, proj_data)

        projects = ProjectService.get_projects(db, profile.id)
        assert len(projects) == 1


class TestCertificationService:
    """Tests for CertificationService"""

    def test_add_certification(self, db: Session, test_user_id: uuid.UUID):
        """Test adding a certification"""
        profile = ProfileService.create_or_get_profile(db, test_user_id)
        cert_data = CertificationCreate(
            certification_name="AWS Certified Developer",
            issuing_organization="Amazon",
        )
        certification = CertificationService.add_certification(db, profile.id, cert_data)
        assert certification.certification_name == "AWS Certified Developer"

    def test_get_certifications(self, db: Session, test_user_id: uuid.UUID):
        """Test retrieving certifications"""
        profile = ProfileService.create_or_get_profile(db, test_user_id)
        cert_data = CertificationCreate(certification_name="Cert 1")
        CertificationService.add_certification(db, profile.id, cert_data)

        certifications = CertificationService.get_certifications(db, profile.id)
        assert len(certifications) == 1
