"""
Tests for resume optimization services
"""

import uuid
from datetime import date
import pytest
from sqlalchemy.orm import Session

from app.services.optimization_service import (
    OptimizationService,
    ATSService,
    KeywordService,
    FormattingService,
    ReadabilityService,
)
from app.services.tailoring_service import TailoringService
from app.services.job_service import JobService
from app.schemas.job import JobCreate


class TestATSService:
    """Tests for ATS optimization service"""

    def test_calculate_ats_score(self):
        """Test ATS score calculation"""
        content = """
        JOHN DOE
        Email: john@example.com | Phone: (555) 123-4567
        
        PROFESSIONAL EXPERIENCE
        Senior Software Engineer | Tech Corp | 2020-2024
        - Developed APIs using Python and FastAPI
        - Led team of 5 engineers
        
        EDUCATION
        BS Computer Science | University
        """
        score = ATSService.calculate_ats_score(content)
        assert 0 <= score <= 100

    def test_ats_score_no_special_chars(self):
        """Test ATS score improves without special characters"""
        content_no_special = "JOHN DOE Email john@example.com"
        content_special = "JOHN™ DOE® Email john@example.com"
        
        score_clean = ATSService.calculate_ats_score(content_no_special)
        score_special = ATSService.calculate_ats_score(content_special)
        
        assert score_clean >= score_special


class TestKeywordService:
    """Tests for keyword optimization service"""

    def test_extract_keywords(self):
        """Test keyword extraction"""
        content = "Python developer with expertise in FastAPI and Docker"
        keywords = KeywordService.extract_keywords(content)
        assert "Python" in keywords or "python" in [k.lower() for k in keywords]

    def test_calculate_keyword_score(self):
        """Test keyword score calculation"""
        content = "Python FastAPI Docker Kubernetes"
        score = KeywordService.calculate_keyword_score(content)
        assert 0 <= score <= 100

    def test_keyword_match_for_job(self):
        """Test keyword matching with job description"""
        resume = "Python developer with 5 years experience in FastAPI"
        job = "Looking for Python developer with FastAPI experience"
        
        score, matched, missing = KeywordService.calculate_keyword_score_for_job(resume, job)
        assert len(matched) > 0
        assert 0 <= score <= 100


class TestFormattingService:
    """Tests for formatting optimization service"""

    def test_calculate_formatting_score(self):
        """Test formatting score calculation"""
        content = """
        JOHN DOE
        john@example.com
        
        EXPERIENCE
        • Senior Engineer (2020-2024)
        • Led team projects
        
        EDUCATION
        • BS Computer Science
        """
        score = FormattingService.calculate_formatting_score(content)
        assert 0 <= score <= 100

    def test_improve_formatting(self):
        """Test formatting improvements"""
        content = "- Python developer\n- FastAPI expert"
        improved = FormattingService.improve_formatting(content)
        assert "•" in improved


class TestReadabilityService:
    """Tests for readability optimization service"""

    def test_calculate_readability_score(self):
        """Test readability score calculation"""
        content = "Developed high-performance APIs using Python and FastAPI"
        score = ReadabilityService.calculate_readability_score(content)
        assert 0 <= score <= 100

    def test_improve_readability(self):
        """Test readability improvements"""
        content = "I was responsible for working on backend APIs"
        improved = ReadabilityService.improve_readability(content)
        assert "Led" in improved or "Developed" in improved


class TestOptimizationService:
    """Tests for main optimization service"""

    def test_analyze_resume(self, db: Session, test_user_id: uuid.UUID):
        """Test resume analysis"""
        content = """
        JOHN DOE
        john@example.com
        
        PROFESSIONAL EXPERIENCE
        Senior Python Developer | Tech Corp | 2020-2024
        - Developed APIs using FastAPI
        - Led development team
        
        EDUCATION
        BS Computer Science | University
        """
        
        optimization = OptimizationService.analyze_resume(db, test_user_id, content)
        assert optimization.user_id == test_user_id
        assert optimization.overall_score is not None
        assert 0 <= optimization.overall_score <= 100
        assert optimization.ats_score is not None
        assert optimization.keyword_score is not None

    def test_analyze_resume_generates_suggestions(self, db: Session, test_user_id: uuid.UUID):
        """Test that analysis generates suggestions"""
        content = "Just some text"  # Poor quality resume
        
        optimization = OptimizationService.analyze_resume(db, test_user_id, content)
        assert len(optimization.suggestions) > 0

    def test_optimize_resume(self, db: Session, test_user_id: uuid.UUID):
        """Test resume optimization"""
        content = "I was responsible for working on backend systems"
        
        OptimizationService.analyze_resume(db, test_user_id, content)
        optimized = OptimizationService.optimize_resume(db, test_user_id, content)
        
        assert optimized is not None
        assert len(optimized) > 0


class TestTailoringService:
    """Tests for resume tailoring service"""

    def test_create_tailored_resume(self, db: Session, test_user_id: uuid.UUID):
        """Test creating tailored resume"""
        job = JobService.create_job(
            db,
            JobCreate(
                title="Python Engineer",
                company_name="Tech Corp",
                description="Looking for Python expert",
                skills_required=["Python", "FastAPI"],
                posted_date=date(2024, 12, 20),
            ),
        )
        
        resume = """
        JOHN DOE
        Python Developer | 5 years experience
        Skills: Python, FastAPI, Django
        """
        
        # Create optimization first
        OptimizationService.analyze_resume(db, test_user_id, resume)
        
        tailored = TailoringService.create_tailored_resume(
            db, test_user_id, job.id, resume
        )
        
        assert tailored.user_id == test_user_id
        assert tailored.job_id == job.id
        assert tailored.tailored_content is not None
        assert tailored.recommendations is not None

    def test_tailored_resume_highlights_keywords(self, db: Session, test_user_id: uuid.UUID):
        """Test that tailoring highlights relevant keywords"""
        job = JobService.create_job(
            db,
            JobCreate(
                title="FastAPI Developer",
                company_name="Corp",
                description="FastAPI microservices",
                skills_required=["FastAPI", "Python"],
                posted_date=date(2024, 12, 20),
            ),
        )
        
        resume = "Python and FastAPI expert"
        OptimizationService.analyze_resume(db, test_user_id, resume)
        
        tailored = TailoringService.create_tailored_resume(
            db, test_user_id, job.id, resume
        )
        
        assert "fastapi" in tailored.tailored_content.lower()

    def test_get_tailored_resume(self, db: Session, test_user_id: uuid.UUID):
        """Test retrieving tailored resume"""
        job = JobService.create_job(
            db,
            JobCreate(
                title="Engineer",
                company_name="Corp",
                posted_date=date(2024, 12, 20),
            ),
        )
        
        resume = "Test resume"
        OptimizationService.analyze_resume(db, test_user_id, resume)
        
        created = TailoringService.create_tailored_resume(
            db, test_user_id, job.id, resume
        )
        
        retrieved = TailoringService.get_tailored_resume(db, test_user_id, job.id)
        assert retrieved.id == created.id
