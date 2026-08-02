"""
Celery tasks for background processing
"""

from .parsing_tasks import (
    parse_resume_task,
    retry_failed_parsing_task,
)

__all__ = [
    "parse_resume_task",
    "retry_failed_parsing_task",
]
