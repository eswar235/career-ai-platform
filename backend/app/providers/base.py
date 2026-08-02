"""
Base AI Provider interface - all providers must implement this
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class AIProviderConfig:
    """Configuration for AI providers"""

    api_key: str
    model: str
    temperature: float = 0.3
    max_tokens: int = 2000
    timeout: int = 30
    max_retries: int = 3
    retry_delay: int = 2  # seconds
    rate_limit_per_minute: int = 60


class AIProviderError(Exception):
    """Base exception for AI provider errors"""

    pass


class AIProviderRateLimitError(AIProviderError):
    """Raised when rate limit is exceeded"""

    pass


class AIProviderTimeoutError(AIProviderError):
    """Raised when request times out"""

    pass


class AIProviderValidationError(AIProviderError):
    """Raised when output validation fails"""

    pass


class BaseAIProvider(ABC):
    """
    Abstract base class for all AI providers.
    
    Implementations must:
    1. Parse resumes into structured data
    2. Handle retries and rate limiting
    3. Return consistent JSON format
    4. Provide usage tracking
    """

    def __init__(self, config: AIProviderConfig):
        """
        Initialize AI provider

        Args:
            config: Provider configuration
        """
        self.config = config
        self.usage_tokens = 0
        self.usage_requests = 0

    @abstractmethod
    async def parse_resume(self, resume_text: str) -> Dict[str, Any]:
        """
        Parse resume text into structured data

        Args:
            resume_text: Extracted resume text

        Returns:
            Dictionary with parsed resume data:
            {
              "full_name": str,
              "email": str,
              "phone": str,
              "location": str,
              "summary": str,
              "skills": [{
                "name": str,
                "proficiency": str,
                "years": int
              }],
              "experience": [{
                "title": str,
                "company": str,
                "start_date": str,
                "end_date": str,
                "description": str
              }],
              "education": [{
                "degree": str,
                "institution": str,
                "year": int,
                "field": str
              }],
              "certifications": [{
                "name": str,
                "issuer": str,
                "year": int
              }]
            }

        Raises:
            AIProviderError: If parsing fails
            AIProviderRateLimitError: If rate limited
            AIProviderTimeoutError: If request times out
        """
        pass

    @abstractmethod
    def create_parsing_prompt(self, resume_text: str) -> str:
        """
        Create the prompt for resume parsing

        Args:
            resume_text: Resume text to parse

        Returns:
            Prompt string for the AI model
        """
        pass

    @abstractmethod
    async def validate_output(self, output: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate AI output

        Args:
            output: Output from AI model

        Returns:
            Tuple of (is_valid, error_message)
        """
        pass

    @abstractmethod
    async def test_connection(self) -> bool:
        """
        Test connection to AI provider

        Args:
            None

        Returns:
            True if connection successful

        Raises:
            AIProviderError: If connection fails
        """
        pass

    def get_usage_stats(self) -> Dict[str, int]:
        """
        Get usage statistics

        Returns:
            Dictionary with usage stats
        """
        return {
            "tokens": self.usage_tokens,
            "requests": self.usage_requests,
        }

    def reset_usage_stats(self) -> None:
        """Reset usage statistics"""
        self.usage_tokens = 0
        self.usage_requests = 0
