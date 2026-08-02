"""
User request/response schemas using Pydantic
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema with common fields"""

    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """Schema for user registration"""

    password: str = Field(
        ...,
        min_length=8,
        description="Password must be at least 8 characters with uppercase, lowercase, and number",
    )

    def validate_password(self) -> bool:
        """Validate password complexity"""
        has_upper = any(c.isupper() for c in self.password)
        has_lower = any(c.islower() for c in self.password)
        has_digit = any(c.isdigit() for c in self.password)

        return has_upper and has_lower and has_digit


class UserLogin(BaseModel):
    """Schema for user login"""

    email: EmailStr
    password: str


class UserResponse(UserBase):
    """Schema for user response"""

    id: UUID
    email_verified: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Schema for token response"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenRefreshRequest(BaseModel):
    """Schema for refresh token request"""

    refresh_token: str


class CurrentUser(UserResponse):
    """Schema for current authenticated user"""

    pass

