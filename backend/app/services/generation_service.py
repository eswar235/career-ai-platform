"""
Cover letter generation service using OpenAI
"""

import logging
import uuid
from typing import Optional

from sqlalchemy.orm import Session

from app.models.cover_letter import CoverLetter, LetterTemplate
from app.models.job import Job
from app.models.profile import UserProfile
from app.models.resume import Resume
from app.providers.openai_provider import OpenAIProvider

logger = logging.getLogger(__name__)


class GenerationService:
    """Service for AI-powered cover letter generation"""

    @staticmethod
    def generate_cover_letter(
        db: Session,
        user_id: uuid.UUID,
        job_id: uuid.UUID,
        template_id: Optional[uuid.UUID] = None,
        use_profile: bool = True,
    ) -> str:
        """Generate a personalized cover letter using AI"""
        try:
            # Get job details
            job = db.query(Job).filter(Job.id == job_id).first()
            if not job:
                raise ValueError("Job not found")

            # Build context from user data
            profile_context = ""
            if use_profile:
                profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
                if profile:
                    profile_context = GenerationService._build_profile_context(profile)

            # Get template if provided
            template_text = ""
            if template_id:
                template = (
                    db.query(LetterTemplate)
                    .filter(
                        LetterTemplate.id == template_id,
                        LetterTemplate.user_id == user_id,
                    )
                    .first()
                )
                if template:
                    template_text = f"\nUse this template as a base:\n{template.content}"

            # Build the prompt
            prompt = GenerationService._build_generation_prompt(
                job=job,
                profile_context=profile_context,
                template_text=template_text,
            )

            # Generate using OpenAI
            provider = OpenAIProvider()
            generated_content = provider.generate_text(
                prompt=prompt,
                model="gpt-3.5-turbo",
                temperature=0.7,
                max_tokens=800,
            )

            if not generated_content:
                raise ValueError("Failed to generate cover letter")

            logger.info(f"Generated cover letter for user {user_id}, job {job_id}")
            return generated_content
        except Exception as e:
            logger.error(f"Error generating cover letter: {str(e)}")
            raise ValueError(f"Failed to generate cover letter: {str(e)}")

    @staticmethod
    def regenerate_cover_letter(
        db: Session,
        user_id: uuid.UUID,
        job_id: uuid.UUID,
    ) -> str:
        """Regenerate a cover letter with a fresh prompt"""
        try:
            # Get the existing letter to track that we're creating a new version
            existing = (
                db.query(CoverLetter)
                .filter(
                    CoverLetter.user_id == user_id,
                    CoverLetter.job_id == job_id,
                )
                .first()
            )

            # Generate fresh content (reusing the generation logic)
            new_content = GenerationService.generate_cover_letter(
                db=db,
                user_id=user_id,
                job_id=job_id,
                use_profile=True,
            )

            logger.info(f"Regenerated cover letter for user {user_id}, job {job_id}")
            return new_content
        except Exception as e:
            logger.error(f"Error regenerating cover letter: {str(e)}")
            raise ValueError(f"Failed to regenerate cover letter: {str(e)}")

    @staticmethod
    def _build_profile_context(profile: UserProfile) -> str:
        """Build context string from user profile"""
        try:
            context_parts = []

            if profile.professional_summary:
                context_parts.append(f"Professional Summary: {profile.professional_summary}")

            if profile.target_role:
                context_parts.append(f"Target Role: {profile.target_role}")

            if profile.career_goals:
                context_parts.append(f"Career Goals: {profile.career_goals}")

            # Add skills if available
            if profile.skills:
                skill_names = [skill.name for skill in profile.skills]
                context_parts.append(f"Key Skills: {', '.join(skill_names)}")

            return "\n".join(context_parts)
        except Exception as e:
            logger.warning(f"Error building profile context: {str(e)}")
            return ""

    @staticmethod
    def _build_generation_prompt(
        job: Job,
        profile_context: str,
        template_text: str,
    ) -> str:
        """Build the prompt for cover letter generation"""
        prompt = f"""Generate a professional, personalized cover letter for the following job opportunity.

Job Title: {job.title}
Company: {job.company}
Job Description: {job.description[:1000]}

{f"Candidate Profile:{profile_context}" if profile_context else ""}

{template_text if template_text else ""}

Requirements:
1. Make it personalized and compelling
2. Highlight relevant skills and experience
3. Show enthusiasm for the role and company
4. Keep it to 3-4 paragraphs
5. Professional tone throughout
6. Start with a strong opening that hooks the reader
7. Include specific examples or achievements when possible

Generate only the cover letter content without any additional commentary."""

        return prompt

    @staticmethod
    def generate_multiple_cover_letters(
        db: Session,
        user_id: uuid.UUID,
        job_ids: list[uuid.UUID],
    ) -> int:
        """Generate cover letters for multiple jobs"""
        generated_count = 0

        for job_id in job_ids:
            try:
                # Check if letter already exists
                existing = (
                    db.query(CoverLetter)
                    .filter(
                        CoverLetter.user_id == user_id,
                        CoverLetter.job_id == job_id,
                    )
                    .first()
                )

                # Skip if already exists
                if existing:
                    continue

                # Generate new letter
                content = GenerationService.generate_cover_letter(
                    db=db,
                    user_id=user_id,
                    job_id=job_id,
                )

                generated_count += 1
            except Exception as e:
                logger.warning(f"Failed to generate letter for job {job_id}: {str(e)}")
                continue

        logger.info(f"Generated {generated_count} cover letters for user {user_id}")
        return generated_count
