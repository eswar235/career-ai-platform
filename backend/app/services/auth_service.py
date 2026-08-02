"""
Authentication business logic service
"""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.security import SecurityService
from app.models.user import User
from app.schemas.user import UserCreate


class AuthService:
    """Handles authentication business logic"""

    @staticmethod
    def register_user(db: Session, user_create: UserCreate) -> User:
        """
        Register a new user
        
        Args:
            db: Database session
            user_create: User registration data
            
        Returns:
            Created user
            
        Raises:
            ValueError: If email already exists
        """
        # Check if email already exists
        existing_user = db.query(User).filter(User.email == user_create.email).first()
        if existing_user:
            raise ValueError(f"Email {user_create.email} already registered")

        # Validate password complexity
        if not user_create.validate_password():
            raise ValueError(
                "Password must contain uppercase, lowercase, and numeric characters"
            )

        # Hash password and create user
        hashed_password = SecurityService.hash_password(user_create.password)

        db_user = User(
            email=user_create.email,
            hashed_password=hashed_password,
            full_name=user_create.full_name,
            email_verified=False,
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        return db_user

    @staticmethod
    def authenticate_user(
        db: Session,
        email: str,
        password: str,
    ) -> Optional[User]:
        """
        Authenticate user by email and password
        
        Args:
            db: Database session
            email: User email
            password: User password
            
        Returns:
            User if authentication successful, None otherwise
        """
        # Find user by email
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return None

        # Verify password
        if not SecurityService.verify_password(password, user.hashed_password):
            return None

        # Check if account is active
        if not user.is_active:
            return None

        # Update last login
        user.update_last_login()
        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def get_user_by_id(db: Session, user_id: UUID) -> Optional[User]:
        """
        Get user by ID
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            User if found, None otherwise
        """
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """
        Get user by email
        
        Args:
            db: Database session
            email: User email
            
        Returns:
            User if found, None otherwise
        """
        return db.query(User).filter(User.email == email).first()

