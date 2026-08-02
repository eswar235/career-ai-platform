"""
Job matching service for AI-powered job recommendations using embeddings
"""

import logging
import uuid
import json
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from app.models.matching import ResumeEmbedding, JobEmbedding, JobMatch
from app.models.job import Job
from app.models.profile import UserProfile, ProfileSkill
from app.schemas.matching import SkillAnalysis

logger = logging.getLogger(__name__)

# Placeholder for OpenAI embeddings - in production use real API
EMBEDDING_DIMENSION = 1536


class EmbeddingService:
    """Service for creating and managing embeddings"""

    @staticmethod
    def create_embedding(text: str) -> list[float]:
        """
        Create embedding for text using OpenAI API
        In production, call: response = openai.Embedding.create(input=text, model="text-embedding-3-small")
        """
        # Placeholder implementation - returns random vector for testing
        import random
        return [random.uniform(-1, 1) for _ in range(EMBEDDING_DIMENSION)]

    @staticmethod
    def create_resume_embedding(
        db: Session,
        user_id: uuid.UUID,
    ) -> ResumeEmbedding:
        """Create or update resume embedding for user"""
        # Get user profile and skills
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        if not profile:
            raise ValueError("User profile not found")

        # Get skills
        skills = db.query(ProfileSkill).filter(ProfileSkill.profile_id == profile.id).all()
        extracted_skills = [skill.skill_name for skill in skills]

        # Build content for embedding
        content_parts = [
            profile.headline or "",
            profile.professional_summary or "",
            " ".join(extracted_skills),
        ]
        content = " ".join(filter(None, content_parts))

        # Create embedding
        embedding_vector = EmbeddingService.create_embedding(content)

        # Check if embedding exists
        existing = (
            db.query(ResumeEmbedding)
            .filter(ResumeEmbedding.user_id == user_id)
            .first()
        )

        if existing:
            existing.content = content
            existing.embedding = embedding_vector
            existing.skills_extracted = extracted_skills
            existing.experience_summary = profile.professional_summary
            existing.updated_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(existing)
            logger.info(f"Resume embedding updated for user {user_id}")
            return existing
        else:
            resume_embedding = ResumeEmbedding(
                user_id=user_id,
                content=content,
                embedding=embedding_vector,
                skills_extracted=extracted_skills,
                experience_summary=profile.professional_summary,
            )
            db.add(resume_embedding)
            db.commit()
            db.refresh(resume_embedding)
            logger.info(f"Resume embedding created for user {user_id}")
            return resume_embedding

    @staticmethod
    def create_job_embedding(db: Session, job_id: uuid.UUID) -> JobEmbedding:
        """Create or update job embedding"""
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise ValueError("Job not found")

        # Build content for embedding
        content_parts = [
            job.title,
            job.description or "",
            job.requirements or "",
            " ".join(job.skills_required or []),
        ]
        content = " ".join(filter(None, content_parts))

        # Normalize skills
        skills_normalized = [skill.lower() for skill in job.skills_required or []]

        # Create embedding
        embedding_vector = EmbeddingService.create_embedding(content)

        # Check if embedding exists
        existing = (
            db.query(JobEmbedding).filter(JobEmbedding.job_id == job_id).first()
        )

        if existing:
            existing.content = content
            existing.embedding = embedding_vector
            existing.skills_required_normalized = skills_normalized
            existing.updated_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(existing)
            logger.info(f"Job embedding updated for job {job_id}")
            return existing
        else:
            job_embedding = JobEmbedding(
                job_id=job_id,
                content=content,
                embedding=embedding_vector,
                skills_required_normalized=skills_normalized,
            )
            db.add(job_embedding)
            db.commit()
            db.refresh(job_embedding)
            logger.info(f"Job embedding created for job {job_id}")
            return job_embedding


class SkillAnalysisService:
    """Service for analyzing skill matches and gaps"""

    @staticmethod
    def normalize_skill(skill: str) -> str:
        """Normalize skill name for comparison"""
        return skill.lower().strip()

    @staticmethod
    def analyze_skills(
        db: Session,
        user_id: uuid.UUID,
        job_id: uuid.UUID,
    ) -> SkillAnalysis:
        """Analyze skill match between user and job"""
        # Get user skills
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        if not profile:
            raise ValueError("User profile not found")

        user_skills_objs = (
            db.query(ProfileSkill)
            .filter(ProfileSkill.profile_id == profile.id)
            .all()
        )
        user_skills = [
            SkillAnalysisService.normalize_skill(s.skill_name)
            for s in user_skills_objs
        ]

        # Get job skills
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise ValueError("Job not found")

        job_skills = [
            SkillAnalysisService.normalize_skill(s)
            for s in (job.skills_required or [])
        ]

        # Find matches
        matched_skills = [s for s in user_skills if s in job_skills]
        missing_skills = [s for s in job_skills if s not in user_skills]

        # Calculate percentages
        total_required = len(job_skills) if job_skills else 1
        skill_match_percentage = (len(matched_skills) / total_required) * 100

        return SkillAnalysis(
            user_skills=user_skills,
            job_required_skills=job_skills,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            match_count=len(matched_skills),
            missing_count=len(missing_skills),
            skill_match_percentage=skill_match_percentage,
        )


class MatchingService:
    """Service for computing job matches"""

    @staticmethod
    def cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        if not vec1 or not vec2:
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = sum(a * a for a in vec1) ** 0.5
        magnitude2 = sum(b * b for b in vec2) ** 0.5

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        return dot_product / (magnitude1 * magnitude2)

    @staticmethod
    def compute_match(
        db: Session,
        user_id: uuid.UUID,
        job_id: uuid.UUID,
    ) -> JobMatch:
        """Compute and store job match"""
        # Get embeddings
        resume_emb = (
            db.query(ResumeEmbedding)
            .filter(ResumeEmbedding.user_id == user_id)
            .first()
        )
        if not resume_emb:
            # Create if doesn't exist
            resume_emb = EmbeddingService.create_resume_embedding(db, user_id)

        job_emb = db.query(JobEmbedding).filter(JobEmbedding.job_id == job_id).first()
        if not job_emb:
            # Create if doesn't exist
            job_emb = EmbeddingService.create_job_embedding(db, job_id)

        # Calculate similarity score
        resume_vec = resume_emb.embedding or []
        job_vec = job_emb.embedding or []
        similarity_score = MatchingService.cosine_similarity(resume_vec, job_vec)

        # Analyze skills
        skill_analysis = SkillAnalysisService.analyze_skills(db, user_id, job_id)

        # Combine scores (70% embedding similarity + 30% skill match)
        skill_percentage = skill_analysis.skill_match_percentage / 100.0
        combined_score = (similarity_score * 0.7) + (skill_percentage * 0.3)
        match_percentage = min(100, max(0, int(combined_score * 100)))

        # Generate strengths, gaps, recommendations
        strengths = MatchingService._generate_strengths(skill_analysis)
        gaps = skill_analysis.missing_skills[:5]  # Top 5 gaps
        recommendations = MatchingService._generate_recommendations(
            skill_analysis, db, user_id
        )

        # Check if match exists
        existing = (
            db.query(JobMatch)
            .filter(
                and_(
                    JobMatch.user_id == user_id,
                    JobMatch.job_id == job_id,
                )
            )
            .first()
        )

        if existing:
            existing.match_percentage = match_percentage
            existing.match_score = float(combined_score)
            existing.skills_match = skill_analysis.match_count
            existing.skills_missing = skill_analysis.missing_count
            existing.strengths = strengths
            existing.gaps = gaps
            existing.recommendations = recommendations
            existing.updated_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(existing)
            logger.info(f"Match updated: user={user_id}, job={job_id}, score={match_percentage}%")
            return existing
        else:
            job_match = JobMatch(
                user_id=user_id,
                job_id=job_id,
                match_percentage=match_percentage,
                match_score=float(combined_score),
                skills_match=skill_analysis.match_count,
                skills_missing=skill_analysis.missing_count,
                strengths=strengths,
                gaps=gaps,
                recommendations=recommendations,
            )
            db.add(job_match)
            db.commit()
            db.refresh(job_match)
            logger.info(f"Match created: user={user_id}, job={job_id}, score={match_percentage}%")
            return job_match

    @staticmethod
    def _generate_strengths(skill_analysis: SkillAnalysis) -> list[str]:
        """Generate list of user strengths based on skill match"""
        strengths = []

        if skill_analysis.skill_match_percentage >= 80:
            strengths.append("Strong skill alignment")
        elif skill_analysis.skill_match_percentage >= 50:
            strengths.append("Good skill overlap")

        if skill_analysis.match_count >= 5:
            strengths.append(f"Matched {skill_analysis.match_count} key skills")

        if not strengths:
            strengths.append("Potential to learn required skills")

        return strengths

    @staticmethod
    def _generate_recommendations(
        skill_analysis: SkillAnalysis,
        db: Session,
        user_id: uuid.UUID,
    ) -> list[str]:
        """Generate recommendations for skill improvement"""
        recommendations = []

        if skill_analysis.missing_skills:
            top_missing = skill_analysis.missing_skills[:3]
            recommendations.append(f"Learn: {', '.join(top_missing)}")

        if skill_analysis.skill_match_percentage < 50:
            recommendations.append("Consider upskilling before applying")

        if skill_analysis.missing_count > 0:
            recommendations.append(
                f"Fill {skill_analysis.missing_count} skill gap(s) for better match"
            )

        if not recommendations:
            recommendations.append("You're well-prepared for this role!")

        return recommendations

    @staticmethod
    def get_match(db: Session, user_id: uuid.UUID, job_id: uuid.UUID) -> JobMatch | None:
        """Get existing match"""
        return (
            db.query(JobMatch)
            .filter(
                and_(
                    JobMatch.user_id == user_id,
                    JobMatch.job_id == job_id,
                )
            )
            .first()
        )

    @staticmethod
    def get_user_matches(
        db: Session,
        user_id: uuid.UUID,
        min_percentage: int = 0,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[int, list[JobMatch]]:
        """Get user's top job matches"""
        query = db.query(JobMatch).filter(
            and_(
                JobMatch.user_id == user_id,
                JobMatch.match_percentage >= min_percentage,
            )
        )

        total = query.count()
        matches = (
            query.order_by(desc(JobMatch.match_percentage))
            .offset(skip)
            .limit(limit)
            .all()
        )

        return total, matches

    @staticmethod
    def compute_bulk_matches(
        db: Session,
        user_id: uuid.UUID,
    ) -> dict:
        """Compute matches for all active jobs"""
        jobs = db.query(Job).filter(Job.is_active == True).all()

        total = len(jobs)
        high_matches = 0
        moderate_matches = 0
        low_matches = 0

        for job in jobs:
            match = MatchingService.compute_match(db, user_id, job.id)

            if match.match_percentage > 75:
                high_matches += 1
            elif match.match_percentage >= 50:
                moderate_matches += 1
            else:
                low_matches += 1

        logger.info(
            f"Bulk matching complete for user {user_id}: high={high_matches}, moderate={moderate_matches}, low={low_matches}"
        )

        return {
            "total_matches": total,
            "matched_jobs": total,
            "high_matches": high_matches,
            "moderate_matches": moderate_matches,
            "low_matches": low_matches,
        }
