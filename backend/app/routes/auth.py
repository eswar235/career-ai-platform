"""
Authentication API endpoints
"""

from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import SecurityService
from app.schemas.user import (
    CurrentUser,
    TokenRefreshRequest,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
)
from app.services.auth_service import AuthService
from app.models.user import User

router = APIRouter(
    prefix="/api/auth",
    tags=["authentication"],
)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_create: UserCreate,
    db: Session = Depends(get_db),
) -> UserResponse:
    """
    Register a new user
    
    Args:
        user_create: User registration data
        db: Database session
        
    Returns:
        Created user
        
    Raises:
        HTTPException: If email already exists or validation fails
    """
    try:
        user = AuthService.register_user(db, user_create)
        return UserResponse.from_attributes(user)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin,
    db: Session = Depends(get_db),
) -> TokenResponse:
    """
    Authenticate user and return tokens
    
    Args:
        credentials: User login credentials
        db: Database session
        
    Returns:
        Access and refresh tokens
        
    Raises:
        HTTPException: If credentials are invalid
    """
    # Authenticate user
    user = AuthService.authenticate_user(db, credentials.email, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create tokens
    access_token = SecurityService.create_access_token(subject=str(user.id))
    refresh_token = SecurityService.create_refresh_token(subject=str(user.id))

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=int(3600),  # 1 hour in seconds
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: TokenRefreshRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    """
    Refresh access token using refresh token
    
    Args:
        request: Refresh token request
        db: Database session
        
    Returns:
        New access and refresh tokens
        
    Raises:
        HTTPException: If refresh token is invalid
    """
    # Verify refresh token
    user_id_str = SecurityService.verify_token(
        request.refresh_token,
        token_type="refresh",
    )
    if user_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify user still exists
    try:
        from uuid import UUID
        user_id = UUID(user_id_str)
        user = AuthService.get_user_by_id(db, user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    # Create new tokens
    access_token = SecurityService.create_access_token(subject=str(user.id))
    refresh_token = SecurityService.create_refresh_token(subject=str(user.id))

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=int(3600),
    )


@router.get("/me", response_model=CurrentUser)
async def get_current_user(
    authorization: Annotated[str, Header()] = None,
    db: Session = Depends(get_db),
) -> CurrentUser:
    """
    Get current authenticated user
    
    Args:
        authorization: Authorization header (Bearer <token>)
        db: Database session
        
    Returns:
        Current user
        
    Raises:
        HTTPException: If not authenticated
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract token
    token = authorization.split(" ")[1]

    # Verify token
    user_id_str = SecurityService.verify_token(token, token_type="access")
    if user_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user
    try:
        from uuid import UUID
        user_id = UUID(user_id_str)
        user = AuthService.get_user_by_id(db, user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return CurrentUser.from_attributes(user)


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    authorization: Annotated[str, Header()] = None,
) -> dict:
    """
    Logout user (client-side token removal)
    
    Args:
        authorization: Authorization header (Bearer <token>)
        
    Returns:
        Success message
    """
    # In this implementation, logout is handled client-side by removing tokens
    # In production, you might implement token blacklisting
    return {"message": "Successfully logged out"}

