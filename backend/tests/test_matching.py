"""
Tests for job matching and embeddings services
"""

import uuid
from datetime import date
import pytest
from sqlalchemy.orm import Session

from app.services.matching_service import (
    EmbeddingService,
    SkillAnalysisService,
    MatchingService,
)
from app.services.job_service import JobService
from app.schemas.job import JobCreate
from app.models.profile import UserProfile, ProfileSkill


class TestEmbeddingService:
    """Tests for EmbeddingService"""

    def test_create_embedding(self):
        """Test creating an embedding vector"""
        text = "Senior Python developer with 5 years experience"
        embedding = EmbeddingService.create_embedding(text)
        assert isinstance(embedding, list)
        assert len(embedding) == 1536  # OpenAI embedding dimension

    def test_create_resume_embedding(self, db: Session, test_user_id: uuid.UUID):
        """Test creating resume embedding"""
        from app.services.profile_service import ProfileService, SkillService
        from app.schemas.profile import SkillCreate

        # Create profile and skills
        profile = ProfileService.create_or_get_profile(db, test_user_id)
        SkillService.add_skill(db, profile.id, SkillCreate(skill_name="Python"))
        SkillService.add_skill(db, profile.id, SkillCreate(skill_name="FastAPI"))

        # Create embedding
        resume_emb = EmbeddingService.create_resume_embedding(db, test_user_id)
        assert resume_emb.user_id == test_user_id
        assert resume_emb.skills_extracted == ["Python", "FastAPI"]
        assert resume_emb.embedding is not None

    def test_create_job_embedding(self, db: Session):
        """Test creating job embedding"""
        job = JobService.create_job(
            db,
            JobCreate(
                title="Python Engineer",
                company_name="Tech Corp",
                skills_required=["Python", "FastAPI", "PostgreSQL"],
                posted_date=date(2024, 12, 20),
            ),
        )

        job_emb = EmbeddingService.create_job_embedding(db, job.id)
        assert job_emb.job_id == job.id
        assert "python" in job_emb.skills_required_normalized
        assert job_emb.embedding is not None


class TestSkillAnalysisService:
    """Tests for SkillAnalysisService"""

    def test_normalize_skill(self):
        """Test skill normalization"""
        skill = "  Python  "
        normalized = SkillAnalysisService.normalize_skill(skill)
        assert normalized == "python"

    def test_analyze_skills_perfect_match(self, db: Session, test_user_id: uuid.UUID):
        """Test analyzing skills with perfect match"""
        from app.services.profile_service import ProfileService, SkillService
        from app.schemas.profile import SkillCreate

        # Create profile with skills
        profile = ProfileService.create_or_get_profile(db, test_user_id)
        SkillService.add_skill(db, profile.id, SkillCreate(skill_name="Python"))
        SkillService.add_skill(db, profile.id, SkillCreate(skill_name="FastAPI"))

        # Create job
        job = JobService.create_job(
            db,
            JobCreate(
                title="Engineer",
                company_name="Corp",
                skills_required=["Python", "FastAPI"],
                posted_date=date(2024, 12, 20),
            ),
        )

        # Analyze
        analysis = SkillAnalysisService.analyze_skills(db, test_user_id, job.id)
        assert analysis.match_count == 2
        assert analysis.missing_count == 0
        assert analysis.skill_match_percentage == 100.0

    def test_analyze_skills_partial_match(self, db: Session, test_user_id: uuid.UUID):
        """Test analyzing skills with partial match"""
        from app.services.profile_service import ProfileService, SkillService
        from app.schemas.profile import SkillCreate

        # Create profile with some skills
        profile = ProfileService.create_or_get_profile(db, test_user_id)
        SkillService.add_skill(db, profile.id, SkillCreate(skill_name="Python"))

        # Create job requiring more skills
        job = JobService.create_job(
            db,
            JobCreate(
                title="Engineer",
                company_name="Corp",
                skills_required=["Python", "FastAPI", "PostgreSQL"],
                posted_date=date(2024, 12, 20),
            ),
        )

        # Analyze
        analysis = SkillAnalysisService.analyze_skills(db, test_user_id, job.id)
        assert analysis.match_count == 1
        assert analysis.missing_count == 2
        assert analysis.skill_match_percentage == pytest.approx(33.33, abs=1)

    def test_analyze_skills_no_match(self, db: Session, test_user_id: uuid.UUID):
        """Test analyzing skills with no match"""
        from app.services.profile_service import ProfileService

        # Create profile without skills
        profile = ProfileService.create_or_get_profile(db, test_user_id)

        # Create job
        job = JobService.create_job(
            db,
            JobCreate(
                title="Engineer",
                company_name="Corp",
                skills_required=["Python", "FastAPI"],
                posted_date=date(2024, 12, 20),
            ),
        )

        # Analyze
        analysis = SkillAnalysisService.analyze_skills(db, test_user_id, job.id)
        assert analysis.match_count == 0
        assert analysis.missing_count == 2


class TestMatchingService:
    """Tests for MatchingService"""

    def test_cosine_similarity(self):
        """Test cosine similarity calculation"""
        vec1 = [1, 0, 0]
        vec2 = [1, 0, 0]
        similarity = MatchingService.cosine_similarity(vec1, vec2)
        assert similarity == pytest.approx(1.0)

    def test_cosine_similarity_orthogonal(self):
        """Test cosine similarity of orthogonal vectors"""
        vec1 = [1, 0, 0]
        vec2 = [0, 1, 0]
        similarity = MatchingService.cosine_similarity(vec1, vec2)
        assert similarity == pytest.approx(0.0)

    def test_compute_match(self, db: Session, test_user_id: uuid.UUID):
        """Test computing a job match"""
        from app.services.profile_service import ProfileService, SkillService
        from app.schemas.profile import SkillCreate

        # Create profile with skills
        profile = ProfileService.create_or_get_profile(db, test_user_id)
        SkillService.add_skill(db, profile.id, SkillCreate(skill_name="Python"))

        # Create job
        job = JobService.create_job(
            db,
            JobCreate(
                title="Python Engineer",
                company_name="Tech Corp",
                skills_required=["Python"],
                posted_date=date(2024, 12, 20),
            ),
        )

        # Compute match
        match = MatchingService.compute_match(db, test_user_id, job.id)
        assert match.user_id == test_user_id
        assert match.job_id == job.id
        assert 0 <= match.match_percentage <= 100
        assert 0.0 <= match.match_score <= 1.0
        assert match.strengths is not None
        assert match.gaps is not None
        assert match.recommendations is not None

    def test_compute_bulk_matches(self, db: Session, test_user_id: uuid.UUID):
        """Test computing bulk matches"""
        from app.services.profile_service import ProfileService

        # Create profile
        profile = ProfileService.create_or_get_profile(db, test_user_id)

        # Create some jobs
        for i in range(3):
            JobService.create_job(
                db,
                JobCreate(
                    title=f"Job {i}",
                    company_name="Corp",
                    posted_date=date(2024, 12, 20),
                ),
            )

        # Compute bulk
        stats = MatchingService.compute_bulk_matches(db, test_user_id)
        assert stats["total_matches"] == 3
        assert stats["matched_jobs"] == 3

    def test_get_user_matches(self, db: Session, test_user_id: uuid.UUID):
        """Test getting user matches"""
        from app.services.profile_service import ProfileService, SkillService
        from app.schemas.profile import SkillCreate

        # Create profile with skills
        profile = ProfileService.create_or_get_profile(db, test_user_id)
        SkillService.add_skill(db, profile.id, SkillCreate(skill_name="Python"))

        # Create jobs
        job1 = JobService.create_job(
            db,
            JobCreate(
                title="Job 1",
                company_name="Corp",
                skills_required=["Python"],
                posted_date=date(2024, 12, 20),
            ),
        )
        job2 = JobService.create_job(
            db,
            JobCreate(
                title="Job 2",
                company_name="Corp",
                skills_required=["Java"],
                posted_date=date(2024, 12, 20),
            ),
        )

        # Compute matches
        MatchingService.compute_match(db, test_user_id, job1.id)
        MatchingService.compute_match(db, test_user_id, job2.id)

        # Get matches
        total, matches = MatchingService.get_user_matches(db, test_user_id)
        assert total == 2
        assert len(matches) > 0
