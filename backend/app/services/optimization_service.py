"""
Resume optimization service for analyzing and improving resumes
"""

import logging
import uuid
import re
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.optimization import ResumeOptimization, TailoredResume, OptimizationSuggestion
from app.models.job import Job
from app.schemas.optimization import KeywordAnalysis

logger = logging.getLogger(__name__)


class OptimizationService:
    """Main optimization service"""

    @staticmethod
    def analyze_resume(
        db: Session,
        user_id: uuid.UUID,
        resume_content: str,
    ) -> ResumeOptimization:
        """Analyze resume and generate optimization report"""
        # Check if exists
        existing = (
            db.query(ResumeOptimization)
            .filter(ResumeOptimization.user_id == user_id)
            .first()
        )

        # Calculate scores
        ats_score = ATSService.calculate_ats_score(resume_content)
        keyword_score = KeywordService.calculate_keyword_score(resume_content)
        formatting_score = FormattingService.calculate_formatting_score(resume_content)
        readability_score = ReadabilityService.calculate_readability_score(resume_content)

        # Overall score (average)
        overall_score = int(
            (ats_score + keyword_score + formatting_score + readability_score) / 4
        )

        if existing:
            existing.original_content = resume_content
            existing.ats_score = ats_score
            existing.keyword_score = keyword_score
            existing.formatting_score = formatting_score
            existing.readability_score = readability_score
            existing.overall_score = overall_score
            existing.updated_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(existing)
            logger.info(f"Resume analysis updated for user {user_id}: score={overall_score}")
            return existing
        else:
            optimization = ResumeOptimization(
                user_id=user_id,
                original_content=resume_content,
                ats_score=ats_score,
                keyword_score=keyword_score,
                formatting_score=formatting_score,
                readability_score=readability_score,
                overall_score=overall_score,
            )
            db.add(optimization)
            db.commit()
            db.refresh(optimization)

            # Generate suggestions
            OptimizationService._generate_suggestions(db, optimization)

            logger.info(f"Resume analysis created for user {user_id}: score={overall_score}")
            return optimization

    @staticmethod
    def _generate_suggestions(
        db: Session,
        optimization: ResumeOptimization,
    ) -> None:
        """Generate optimization suggestions"""
        suggestions = []

        # ATS suggestions
        if optimization.ats_score and optimization.ats_score < 70:
            suggestions.append(
                (
                    "ats",
                    "Your resume may have formatting that interferes with ATS parsing",
                    "high",
                    100 - optimization.ats_score,
                )
            )

        # Keyword suggestions
        if optimization.keyword_score and optimization.keyword_score < 60:
            suggestions.append(
                (
                    "keywords",
                    "Add more industry-relevant keywords to improve visibility",
                    "high",
                    100 - optimization.keyword_score,
                )
            )

        # Formatting suggestions
        if optimization.formatting_score and optimization.formatting_score < 75:
            suggestions.append(
                (
                    "formatting",
                    "Improve resume formatting for better readability",
                    "medium",
                    100 - optimization.formatting_score,
                )
            )

        # Readability suggestions
        if optimization.readability_score and optimization.readability_score < 75:
            suggestions.append(
                (
                    "readability",
                    "Use action verbs and shorter sentences for better readability",
                    "medium",
                    100 - optimization.readability_score,
                )
            )

        # Save suggestions
        for category, text, priority, impact in suggestions:
            suggestion = OptimizationSuggestion(
                optimization_id=optimization.id,
                category=category,
                suggestion=text,
                priority=priority,
                impact_score=impact,
            )
            db.add(suggestion)

        db.commit()
        logger.info(f"Generated {len(suggestions)} suggestions for optimization {optimization.id}")

    @staticmethod
    def optimize_resume(
        db: Session,
        user_id: uuid.UUID,
        resume_content: str,
    ) -> str:
        """Generate optimized version of resume"""
        optimized = resume_content

        # Apply optimizations
        optimized = FormattingService.improve_formatting(optimized)
        optimized = KeywordService.enhance_keywords(optimized)
        optimized = ReadabilityService.improve_readability(optimized)

        # Save optimized version
        optimization = db.query(ResumeOptimization).filter(
            ResumeOptimization.user_id == user_id
        ).first()
        if optimization:
            optimization.optimized_content = optimized
            optimization.updated_at = datetime.now(timezone.utc)
            db.commit()

        logger.info(f"Resume optimized for user {user_id}")
        return optimized

    @staticmethod
    def get_optimization(db: Session, user_id: uuid.UUID) -> ResumeOptimization | None:
        """Get user's resume optimization"""
        return (
            db.query(ResumeOptimization)
            .filter(ResumeOptimization.user_id == user_id)
            .first()
        )


class ATSService:
    """ATS (Applicant Tracking System) optimization service"""

    @staticmethod
    def calculate_ats_score(resume_content: str) -> int:
        """Calculate ATS compatibility score"""
        score = 50  # Base score

        # Check for no tables (good for ATS)
        if "<table" not in resume_content.lower():
            score += 10

        # Check for standard headers
        headers = ["experience", "education", "skills", "contact"]
        found_headers = sum(1 for h in headers if h in resume_content.lower())
        score += found_headers * 5

        # Check for no special formatting
        special_chars = len(re.findall(r"[®™©†‡]", resume_content))
        if special_chars == 0:
            score += 10
        else:
            score -= special_chars * 2

        # Check for standard fonts (simple heuristic)
        if ".pdf" in resume_content.lower() or ".docx" in resume_content.lower():
            score += 5

        return min(100, max(0, score))

    @staticmethod
    def identify_ats_issues(resume_content: str) -> list[str]:
        """Identify ATS parsing issues"""
        issues = []

        if "<table" in resume_content.lower():
            issues.append("Resume contains tables which may not parse correctly in ATS")

        if len(re.findall(r"[^a-zA-Z0-9\s.,\-]", resume_content)) > 20:
            issues.append("Resume contains special characters that may cause parsing issues")

        if not any(h in resume_content.lower() for h in ["experience", "education", "skills"]):
            issues.append("Resume missing standard section headers")

        return issues


class KeywordService:
    """Keyword optimization service"""

    INDUSTRY_KEYWORDS = {
        "Software Engineering": [
            "Python", "JavaScript", "Java", "C++", "SQL", "API", "REST",
            "microservices", "cloud", "AWS", "Docker", "Kubernetes",
            "agile", "CI/CD", "testing", "debugging"
        ],
        "Data Science": [
            "Python", "R", "SQL", "machine learning", "deep learning",
            "statistics", "pandas", "numpy", "scikit-learn", "TensorFlow",
            "data visualization", "analytics", "big data"
        ],
        "Product Management": [
            "roadmap", "strategy", "stakeholder management", "user research",
            "A/B testing", "metrics", "OKR", "agile", "wireframing",
            "product development", "go-to-market"
        ],
    }

    @staticmethod
    def calculate_keyword_score(resume_content: str) -> int:
        """Calculate keyword optimization score"""
        content_lower = resume_content.lower()
        found_keywords = 0

        # Count industry keywords
        for keyword in KeywordService.INDUSTRY_KEYWORDS.get("Software Engineering", []):
            if keyword.lower() in content_lower:
                found_keywords += 1

        # Score based on keywords found
        keyword_score = min(100, int((found_keywords / 15) * 100))
        return keyword_score

    @staticmethod
    def extract_keywords(resume_content: str) -> list[str]:
        """Extract keywords from resume"""
        keywords = set()

        # Add industry keywords found
        for keyword_list in KeywordService.INDUSTRY_KEYWORDS.values():
            for keyword in keyword_list:
                if keyword.lower() in resume_content.lower():
                    keywords.add(keyword)

        # Add capitalized words (potential keywords)
        capitalized = re.findall(r"\b[A-Z][a-z]+\b", resume_content)
        keywords.update(capitalized)

        return list(keywords)

    @staticmethod
    def calculate_keyword_score_for_job(
        resume_content: str,
        job_content: str,
    ) -> tuple[int, list[str], list[str]]:
        """Calculate keyword match with job description"""
        resume_keywords = set(w.lower() for w in resume_content.split() if len(w) > 3)
        job_keywords = set(w.lower() for w in job_content.split() if len(w) > 3)

        matched = resume_keywords.intersection(job_keywords)
        missing = job_keywords - resume_keywords

        if job_keywords:
            score = int((len(matched) / len(job_keywords)) * 100)
        else:
            score = 0

        return score, list(matched), list(missing)

    @staticmethod
    def enhance_keywords(resume_content: str) -> str:
        """Enhance resume with relevant keywords"""
        enhanced = resume_content

        # Add keyword suggestions where relevant
        if "Python" in resume_content and "API" not in resume_content:
            enhanced = enhanced.replace(
                "Python",
                "Python (including REST APIs)"
            )

        if "experience" in enhanced.lower() and "agile" not in enhanced.lower():
            enhanced = enhanced.replace(
                "experience",
                "experience in agile environments"
            )

        return enhanced


class FormattingService:
    """Resume formatting optimization service"""

    @staticmethod
    def calculate_formatting_score(resume_content: str) -> int:
        """Calculate formatting quality score"""
        score = 70  # Base score

        # Check line breaks
        lines = resume_content.split("\n")
        if len(lines) < 5:
            score -= 10  # Too short

        # Check for bullet points
        bullets = len(re.findall(r"[•\-\*]", resume_content))
        if bullets >= 10:
            score += 10
        elif bullets == 0:
            score -= 5

        # Check for consistent spacing
        extra_spaces = len(re.findall(r"  +", resume_content))
        if extra_spaces == 0:
            score += 5
        else:
            score -= extra_spaces // 5

        # Check for proper sections
        sections = len(re.findall(r"[A-Z][A-Z\s]+$", resume_content, re.MULTILINE))
        if sections >= 3:
            score += 10

        return min(100, max(0, score))

    @staticmethod
    def improve_formatting(resume_content: str) -> str:
        """Improve resume formatting"""
        improved = resume_content

        # Normalize bullet points
        improved = improved.replace("- ", "• ")
        improved = improved.replace("* ", "• ")

        # Fix extra spaces
        improved = re.sub(r"  +", " ", improved)

        # Add spacing after sections
        improved = re.sub(r"([A-Z][A-Z\s]+)([a-z])", r"\1\n\2", improved)

        return improved


class ReadabilityService:
    """Resume readability optimization service"""

    @staticmethod
    def calculate_readability_score(resume_content: str) -> int:
        """Calculate readability score"""
        score = 70

        sentences = resume_content.split(".")
        if sentences:
            avg_sentence_length = len(resume_content.split()) / len(sentences)
            if 10 <= avg_sentence_length <= 20:
                score += 10
            elif avg_sentence_length > 30:
                score -= 10

        # Check for action verbs
        action_verbs = [
            "developed", "led", "managed", "created", "implemented",
            "designed", "analyzed", "improved", "increased", "decreased"
        ]
        found_verbs = sum(1 for verb in action_verbs if verb in resume_content.lower())
        score += min(10, found_verbs)

        # Check for numbers/metrics
        metrics = len(re.findall(r"\d+%|\$\d+", resume_content))
        score += min(10, metrics)

        return min(100, max(0, score))

    @staticmethod
    def improve_readability(resume_content: str) -> str:
        """Improve resume readability"""
        improved = resume_content

        # Suggest better action verbs
        weak_verbs = {
            "responsible for": "Led",
            "worked on": "Developed",
            "did": "Accomplished",
        }

        for weak, strong in weak_verbs.items():
            improved = improved.replace(weak, strong)

        return improved
