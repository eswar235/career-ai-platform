"""
FastAPI dependencies for authentication and authorization
"""

from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import SecurityService
from app.models.user import User
from app.services.auth_service import AuthService


async def get_current_user(
    token: str = Depends(lambda: None),
    db: Session = Depends(get_db),
) -> User:
    """
    Get current authenticated user from token
    
    Args:
        token: Bearer token
        db: Database session
        
    Returns:
        Current user
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if token is None:
        raise credentials_exception

    # Verify and extract user ID from token
    user_id_str = SecurityService.verify_token(token, token_type="access")
    if user_id_str is None:
        raise credentials_exception

    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise credentials_exception

    # Get user from database
    user = AuthService.get_user_by_id(db, user_id)
    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    return user


def get_current_user_optional(
    db: Session = Depends(get_db),
) -> Optional[User]:
    """
    Get current user if authenticated, otherwise None
    
    Args:
        db: Database session
        
    Returns:
        Current user or None
    """
    # This will be handled by route parameters
    return None

