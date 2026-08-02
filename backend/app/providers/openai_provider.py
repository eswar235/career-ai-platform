"""
OpenAI AI Provider implementation
Provides resume parsing using OpenAI's GPT models
"""

import asyncio
import json
import logging
from typing import Optional, Dict, Any

from openai import AsyncOpenAI, RateLimitError, APITimeoutError

from .base import (
    BaseAIProvider,
    AIProviderConfig,
    AIProviderError,
    AIProviderRateLimitError,
    AIProviderTimeoutError,
    AIProviderValidationError,
)

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseAIProvider):
    """
    OpenAI implementation using GPT-3.5-turbo or GPT-4
    """

    def __init__(self, config: AIProviderConfig):
        """Initialize OpenAI provider"""
        super().__init__(config)
        if not config.api_key:
            raise AIProviderError("OpenAI API key is required")
        self.client = AsyncOpenAI(api_key=config.api_key)

    def create_parsing_prompt(self, resume_text: str) -> str:
        """Create prompt for OpenAI resume parsing"""
        prompt = f"""Extract structured information from this resume text and return valid JSON.

Resume Text:
{resume_text}

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

    async def parse_resume(self, resume_text: str) -> Dict[str, Any]:
        """
        Parse resume using OpenAI

        Args:
            resume_text: Extracted resume text

        Returns:
            Parsed resume data as dictionary

        Raises:
            AIProviderRateLimitError: If rate limited
            AIProviderTimeoutError: If request times out
            AIProviderError: If parsing fails
        """
        prompt = self.create_parsing_prompt(resume_text)
        retries = 0

        while retries < self.config.max_retries:
            try:
                logger.info(f"Parsing resume with OpenAI (attempt {retries + 1})")

                response = await self.client.chat.completions.create(
                    model=self.config.model,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens,
                    timeout=self.config.timeout,
                )

                # Update usage stats
                if hasattr(response, "usage"):
                    self.usage_tokens += response.usage.total_tokens
                self.usage_requests += 1

                # Extract JSON from response
                response_text = response.choices[0].message.content.strip()

                # Try to parse JSON
                parsed_data = json.loads(response_text)

                logger.info("Successfully parsed resume with OpenAI")
                return parsed_data

            except RateLimitError as e:
                retries += 1
                if retries >= self.config.max_retries:
                    logger.error(f"Rate limited after {retries} attempts")
                    raise AIProviderRateLimitError(f"Rate limited: {str(e)}") from e

                logger.warning(f"Rate limited, retrying in {self.config.retry_delay}s...")
                await asyncio.sleep(self.config.retry_delay)

            except APITimeoutError as e:
                retries += 1
                if retries >= self.config.max_retries:
                    logger.error(f"Timeout after {retries} attempts")
                    raise AIProviderTimeoutError(f"Request timed out: {str(e)}") from e

                logger.warning(f"Timeout, retrying in {self.config.retry_delay}s...")
                await asyncio.sleep(self.config.retry_delay)

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {str(e)}")
                raise AIProviderValidationError(f"Invalid JSON from OpenAI: {str(e)}") from e

            except Exception as e:
                logger.error(f"Failed to parse resume with OpenAI: {str(e)}")
                raise AIProviderError(f"OpenAI parsing failed: {str(e)}") from e

        # Should not reach here, but just in case
        raise AIProviderError(f"Failed after {self.config.max_retries} retries")

    async def validate_output(self, output: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate OpenAI output

        Args:
            output: Output dictionary

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check for required fields
            if not isinstance(output, dict):
                return False, "Output must be a dictionary"

            # Check structure
            expected_fields = [
                "full_name",
                "email",
                "phone",
                "location",
                "summary",
                "skills",
                "experience",
                "education",
                "certifications",
            ]

            for field in expected_fields:
                if field not in output:
                    return False, f"Missing required field: {field}"

            # Check array fields
            for field in ["skills", "experience", "education", "certifications"]:
                if not isinstance(output[field], list):
                    return False, f"{field} must be a list"

            return True, None

        except Exception as e:
            return False, f"Validation error: {str(e)}"

    async def test_connection(self) -> bool:
        """
        Test connection to OpenAI

        Returns:
            True if connection successful

        Raises:
            AIProviderError: If connection fails
        """
        try:
            # Make a minimal API call
            response = await self.client.models.list()
            logger.info("OpenAI connection test successful")
            return True

        except Exception as e:
            logger.error(f"OpenAI connection test failed: {str(e)}")
            raise AIProviderError(f"Failed to connect to OpenAI: {str(e)}") from e

    def __repr__(self) -> str:
        return f"OpenAIProvider(model={self.config.model})"
