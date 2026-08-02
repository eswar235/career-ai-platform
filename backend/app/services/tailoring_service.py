"""
Resume tailoring service for job-specific resume optimization
"""

import logging
import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.optimization import TailoredResume
from app.models.job import Job
from app.services.optimization_service import KeywordService

logger = logging.getLogger(__name__)


class TailoringService:
    """Service for creating job-specific tailored resumes"""

    @staticmethod
    def create_tailored_resume(
        db: Session,
        user_id: uuid.UUID,
        job_id: uuid.UUID,
        base_resume: str,
    ) -> TailoredResume:
        """Create or update tailored resume for specific job"""
        # Get job details
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise ValueError("Job not found")

        # Check if tailored version exists
        existing = (
            db.query(TailoredResume)
            .filter(
                and_(
                    TailoredResume.user_id == user_id,
                    TailoredResume.job_id == job_id,
                )
            )
            .first()
        )

        # Tailor resume
        tailored_content = TailoringService._tailor_content(
            base_resume, job
        )

        # Calculate scores
        keyword_score, matched, missing = KeywordService.calculate_keyword_score_for_job(
            tailored_content,
            (job.title + " " + job.description) or "",
        )

        match_keywords = len(matched)

        # Generate recommendations
        recommendations = TailoringService._generate_recommendations(
            matched, missing, job
        )

        if existing:
            existing.tailored_content = tailored_content
            existing.match_keywords = match_keywords
            existing.keyword_score = keyword_score
            existing.recommendations = recommendations
            existing.updated_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(existing)
            logger.info(f"Tailored resume updated: user={user_id}, job={job_id}")
            return existing
        else:
            tailored = TailoredResume(
                user_id=user_id,
                job_id=job_id,
                tailored_content=tailored_content,
                match_keywords=match_keywords,
                keyword_score=keyword_score,
                recommendations=recommendations,
            )
            db.add(tailored)
            db.commit()
            db.refresh(tailored)
            logger.info(f"Tailored resume created: user={user_id}, job={job_id}")
            return tailored

    @staticmethod
    def _tailor_content(resume_content: str, job: Job) -> str:
        """Tailor resume content to match job"""
        tailored = resume_content

        # Reorder summary to match job requirements
        if job.title and "experience" in tailored.lower():
            summary = f"Seeking {job.job_type or 'role'} in {job.title} area"
            tailored = tailored.replace(
                "Professional Summary",
                f"Professional Summary\n{summary}"
            )

        # Add job-relevant skills to top
        if job.skills_required:
            skills_text = ", ".join(job.skills_required[:5])
            if "Skills" in tailored:
                tailored = tailored.replace(
                    "Skills",
                    f"Skills\n{skills_text}"
                )

        # Highlight relevant experience
        if job.description:
            keywords_from_job = set(w.lower() for w in job.description.split() if len(w) > 4)
            for keyword in keywords_from_job:
                if keyword in tailored.lower():
                    # Highlight keyword
                    tailored = tailored.replace(
                        keyword.title(),
                        f"{keyword.title()}*"
                    )

        return tailored

    @staticmethod
    def _generate_recommendations(
        matched_keywords: list[str],
        missing_keywords: list[str],
        job: Job,
    ) -> list[str]:
        """Generate tailoring recommendations"""
        recommendations = []

        # High priority: add missing key skills
        if missing_keywords:
            top_missing = missing_keywords[:3]
            recommendations.append(
                f"Add: {', '.join(top_missing)}"
            )

        # Medium priority: highlight matched skills
        if matched_keywords and len(matched_keywords) >= 5:
            recommendations.append(
                f"Strongly emphasize your {len(matched_keywords)} matched skills"
            )

        # Add job-specific suggestions
        if job.experience_level:
            recommendations.append(
                f"Emphasize {job.experience_level} level experience"
            )

        if job.job_type:
            recommendations.append(
                f"Tailor for {job.job_type} position"
            )

        # Add salary/location suggestions if relevant
        if job.salary_max:
            recommendations.append(
                f"This role offers up to ${job.salary_max:,} - highlight relevant achievements"
            )

        if not recommendations:
            recommendations.append("Your resume is well-matched for this role!")

        return recommendations[:5]  # Top 5 recommendations

    @staticmethod
    def get_tailored_resume(
        db: Session,
        user_id: uuid.UUID,
        job_id: uuid.UUID,
    ) -> TailoredResume | None:
        """Get tailored resume"""
        return (
            db.query(TailoredResume)
            .filter(
                and_(
                    TailoredResume.user_id == user_id,
                    TailoredResume.job_id == job_id,
                )
            )
            .first()
        )

    @staticmethod
    def get_user_tailored_resumes(
        db: Session,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[int, list[TailoredResume]]:
        """Get all tailored resumes for user"""
        query = db.query(TailoredResume).filter(TailoredResume.user_id == user_id)
        total = query.count()
        tailored = query.offset(skip).limit(limit).all()
        return total, tailored

    @staticmethod
    def delete_tailored_resume(
        db: Session,
        user_id: uuid.UUID,
        job_id: uuid.UUID,
    ) -> bool:
        """Delete tailored resume"""
        tailored = (
            db.query(TailoredResume)
            .filter(
                and_(
                    TailoredResume.user_id == user_id,
                    TailoredResume.job_id == job_id,
                )
            )
            .first()
        )
        if not tailored:
            raise ValueError("Tailored resume not found")

        db.delete(tailored)
        db.commit()
        logger.info(f"Tailored resume deleted: user={user_id}, job={job_id}")
        return True
