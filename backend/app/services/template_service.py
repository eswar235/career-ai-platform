"""
Cover letter template service
"""

import logging
import uuid
from typing import Optional, Tuple

from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.cover_letter import LetterTemplate
from app.schemas.cover_letter import (
    LetterTemplateCreate,
    LetterTemplateUpdate,
)

logger = logging.getLogger(__name__)


class TemplateService:
    """Service for letter template management"""

    @staticmethod
    def create_template(
        db: Session,
        user_id: uuid.UUID,
        template_data: LetterTemplateCreate,
    ) -> LetterTemplate:
        """Create a new letter template"""
        try:
            # If marking as default, unset other defaults for this user
            if template_data.is_default:
                db.query(LetterTemplate).filter(
                    LetterTemplate.user_id == user_id,
                    LetterTemplate.is_default == True,
                ).update({LetterTemplate.is_default: False})

            template = LetterTemplate(
                user_id=user_id,
                name=template_data.name,
                content=template_data.content,
                is_default=template_data.is_default,
            )

            db.add(template)
            db.commit()
            db.refresh(template)

            logger.info(f"Created template '{template_data.name}' for user {user_id}")
            return template
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating template: {str(e)}")
            raise ValueError(f"Failed to create template: {str(e)}")

    @staticmethod
    def get_template(
        db: Session,
        template_id: uuid.UUID,
    ) -> Optional[LetterTemplate]:
        """Get a template by ID"""
        try:
            return db.query(LetterTemplate).filter(LetterTemplate.id == template_id).first()
        except Exception as e:
            logger.error(f"Error retrieving template: {str(e)}")
            raise ValueError(f"Failed to retrieve template: {str(e)}")

    @staticmethod
    def get_default_template(
        db: Session,
        user_id: uuid.UUID,
    ) -> Optional[LetterTemplate]:
        """Get the default template for a user"""
        try:
            return (
                db.query(LetterTemplate)
                .filter(
                    LetterTemplate.user_id == user_id,
                    LetterTemplate.is_default == True,
                )
                .first()
            )
        except Exception as e:
            logger.error(f"Error retrieving default template: {str(e)}")
            raise ValueError(f"Failed to retrieve default template: {str(e)}")

    @staticmethod
    def list_templates(
        db: Session,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 20,
    ) -> Tuple[int, list[LetterTemplate]]:
        """List user's templates"""
        try:
            query = db.query(LetterTemplate).filter(LetterTemplate.user_id == user_id)
            total = query.count()

            templates = (
                query.order_by(desc(LetterTemplate.created_at))
                .offset(skip)
                .limit(limit)
                .all()
            )

            return total, templates
        except Exception as e:
            logger.error(f"Error listing templates: {str(e)}")
            raise ValueError(f"Failed to list templates: {str(e)}")

    @staticmethod
    def update_template(
        db: Session,
        template_id: uuid.UUID,
        user_id: uuid.UUID,
        update_data: LetterTemplateUpdate,
    ) -> LetterTemplate:
        """Update a template"""
        try:
            template = (
                db.query(LetterTemplate)
                .filter(
                    LetterTemplate.id == template_id,
                    LetterTemplate.user_id == user_id,
                )
                .first()
            )
            if not template:
                raise ValueError("Template not found")

            # Handle default template
            if update_data.is_default is True and not template.is_default:
                db.query(LetterTemplate).filter(
                    LetterTemplate.user_id == user_id,
                    LetterTemplate.is_default == True,
                ).update({LetterTemplate.is_default: False})

            if update_data.name is not None:
                template.name = update_data.name
            if update_data.content is not None:
                template.content = update_data.content
            if update_data.is_default is not None:
                template.is_default = update_data.is_default

            db.commit()
            db.refresh(template)

            logger.info(f"Updated template {template_id}")
            return template
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating template: {str(e)}")
            raise ValueError(f"Failed to update template: {str(e)}")

    @staticmethod
    def delete_template(
        db: Session,
        template_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> None:
        """Delete a template"""
        try:
            template = (
                db.query(LetterTemplate)
                .filter(
                    LetterTemplate.id == template_id,
                    LetterTemplate.user_id == user_id,
                )
                .first()
            )
            if not template:
                raise ValueError("Template not found")

            db.delete(template)
            db.commit()

            logger.info(f"Deleted template {template_id}")
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting template: {str(e)}")
            raise ValueError(f"Failed to delete template: {str(e)}")
