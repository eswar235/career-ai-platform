"""
Resume parsing service for extracting text from PDFs and using AI for structured extraction
"""

import json
import logging
import re
from typing import Optional

import pdfplumber
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.parsed_resume import ParsedResume
from app.models.resume import Resume

logger = logging.getLogger(__name__)


class PDFExtractionService:
    """Service for extracting text from PDF files"""

    @staticmethod
    def extract_text_from_pdf(file_content: bytes) -> Optional[str]:
        """
        Extract raw text from PDF file

        Args:
            file_content: PDF file as bytes

        Returns:
            Extracted text or None if extraction fails
        """
        try:
            with pdfplumber.open(file_content) as pdf:
                text_parts = []
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        text_parts.append(text)

                full_text = "\n".join(text_parts)
                logger.info(f"Successfully extracted {len(full_text)} characters from PDF")
                return full_text

        except Exception as e:
            logger.error(f"Failed to extract text from PDF: {str(e)}")
            return None


class ResumeParsingService:
    """Service for parsing resumes using AI"""

    @staticmethod
    def create_parsing_prompt(raw_text: str) -> str:
        """
        Create prompt for LLM to parse resume

        Args:
            raw_text: Raw extracted text from PDF

        Returns:
            Formatted prompt for LLM
        """
        prompt = f"""Extract structured information from this resume text and return valid JSON.

Resume Text:
{raw_text}

Extract and return ONLY valid JSON (no markdown, no extra text) with this exact structure:
{{
  "full_name": "string or null",
  "email": "string or null",
  "phone": "string or null",
  "location": "string or null",
  "summary": "string or null",
  "skills": [
    {{"name": "string", "proficiency": "Beginner|Intermediate|Advanced|Expert", "years": number}}
  ],
  "experience": [
    {{
      "title": "string",
      "company": "string",
      "start_date": "string",
      "end_date": "string or 'Present'",
      "description": "string"
    }}
  ],
  "education": [
    {{
      "degree": "string",
      "institution": "string",
      "year": "number or null",
      "field": "string"
    }}
  ],
  "certifications": [
    {{
      "name": "string",
      "issuer": "string",
      "year": "number or null"
    }}
  ]
}}

Rules:
1. Return ONLY the JSON object, no other text
2. Use null for missing fields
3. Extract as much information as possible from the resume
4. For skills, estimate proficiency based on context
5. For experience, try to parse dates
6. Be thorough but accurate
"""
        return prompt

    @staticmethod
    def parse_resume_with_ai(raw_text: str, client) -> Optional[dict]:
        """
        Use OpenAI to parse resume text into structured data

        Args:
            raw_text: Raw text extracted from PDF
            client: OpenAI client instance

        Returns:
            Parsed resume data as dictionary or None if parsing fails
        """
        try:
            prompt = ResumeParsingService.create_parsing_prompt(raw_text)

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                temperature=0.3,  # Lower temperature for more consistent output
                max_tokens=2000,
            )

            # Extract JSON from response
            response_text = response.choices[0].message.content.strip()

            # Try to parse JSON
            parsed_data = json.loads(response_text)

            logger.info("Successfully parsed resume with AI")
            return parsed_data

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Failed to parse resume with AI: {str(e)}")
            return None

    @staticmethod
    def calculate_confidence_score(parsed_data: dict, raw_text: str) -> int:
        """
        Calculate confidence score for parsed data (0-100)

        Args:
            parsed_data: Parsed resume data
            raw_text: Original raw text

        Returns:
            Confidence score (0-100)
        """
        score = 100
        penalties = 0

        # Check for key fields
        if not parsed_data.get("full_name"):
            penalties += 10
        if not parsed_data.get("email"):
            penalties += 5
        if not parsed_data.get("phone"):
            penalties += 5

        # Check for experience
        if not parsed_data.get("experience") or len(parsed_data.get("experience", [])) == 0:
            penalties += 15

        # Check for education
        if not parsed_data.get("education") or len(parsed_data.get("education", [])) == 0:
            penalties += 10

        # Check for skills
        if not parsed_data.get("skills") or len(parsed_data.get("skills", [])) == 0:
            penalties += 10

        # If raw text is very short, lower confidence
        if len(raw_text) < 500:
            penalties += 20

        # Calculate final score
        final_score = max(0, score - penalties)
        return final_score

    @staticmethod
    def create_parsed_resume(
        db: Session,
        resume_id: str,
        user_id: str,
        parsed_data: dict,
        raw_text: str,
        confidence_score: int,
    ) -> ParsedResume:
        """
        Create ParsedResume record in database

        Args:
            db: Database session
            resume_id: Resume ID
            user_id: User ID
            parsed_data: Parsed resume data
            raw_text: Original raw text
            confidence_score: Confidence score (0-100)

        Returns:
            Created ParsedResume object
        """
        parsed_resume = ParsedResume(
            resume_id=resume_id,
            user_id=user_id,
            full_name=parsed_data.get("full_name"),
            email=parsed_data.get("email"),
            phone=parsed_data.get("phone"),
            location=parsed_data.get("location"),
            summary=parsed_data.get("summary"),
            skills=parsed_data.get("skills", []),
            experience=parsed_data.get("experience", []),
            education=parsed_data.get("education", []),
            certifications=parsed_data.get("certifications", []),
            raw_text=raw_text,
            confidence_score=confidence_score,
        )

        db.add(parsed_resume)
        db.commit()
        db.refresh(parsed_resume)

        logger.info(f"Created ParsedResume {parsed_resume.id} for resume {resume_id}")
        return parsed_resume

    @staticmethod
    def get_parsed_resume(
        db: Session,
        resume_id: str,
        user_id: str,
    ) -> Optional[ParsedResume]:
        """
        Get parsed resume by resume ID

        Args:
            db: Database session
            resume_id: Resume ID
            user_id: User ID for verification

        Returns:
            ParsedResume object or None
        """
        return (
            db.query(ParsedResume)
            .filter(
                ParsedResume.resume_id == resume_id,
                ParsedResume.user_id == user_id,
            )
            .first()
        )

    @staticmethod
    def update_parsed_resume(
        db: Session,
        parsed_resume_id: str,
        updates: dict,
    ) -> ParsedResume:
        """
        Update parsed resume with user corrections

        Args:
            db: Database session
            parsed_resume_id: ParsedResume ID
            updates: Dictionary with fields to update

        Returns:
            Updated ParsedResume
        """
        parsed_resume = (
            db.query(ParsedResume).filter(ParsedResume.id == parsed_resume_id).first()
        )

        if not parsed_resume:
            raise ValueError("ParsedResume not found")

        # Update allowed fields
        allowed_fields = {
            "full_name",
            "email",
            "phone",
            "location",
            "summary",
            "skills",
            "experience",
            "education",
            "certifications",
        }

        for field, value in updates.items():
            if field in allowed_fields:
                setattr(parsed_resume, field, value)

        db.commit()
        db.refresh(parsed_resume)

        logger.info(f"Updated ParsedResume {parsed_resume_id}")
        return parsed_resume

    @staticmethod
    def confirm_parsed_resume(
        db: Session,
        parsed_resume_id: str,
    ) -> ParsedResume:
        """
        Confirm parsing (user reviewed and approved)

        Args:
            db: Database session
            parsed_resume_id: ParsedResume ID

        Returns:
            Updated ParsedResume
        """
        parsed_resume = (
            db.query(ParsedResume).filter(ParsedResume.id == parsed_resume_id).first()
        )

        if not parsed_resume:
            raise ValueError("ParsedResume not found")

        parsed_resume.confirm()
        db.commit()
        db.refresh(parsed_resume)

        logger.info(f"Confirmed ParsedResume {parsed_resume_id}")
        return parsed_resume
