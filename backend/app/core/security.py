"""
Security utilities for authentication and password handling
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# Password hashing context
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,
)


class SecurityService:
    """Handles all security-related operations"""

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using bcrypt
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password
        """
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash
        
        Args:
            plain_password: Plain text password to verify
            hashed_password: Hashed password to verify against
            
        Returns:
            True if password matches, False otherwise
        """
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def create_access_token(
        subject: str,
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        """
        Create a JWT access token
        
        Args:
            subject: Subject (usually user ID as string)
            expires_delta: Custom expiration time
            
        Returns:
            Encoded JWT token
        """
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                hours=settings.JWT_EXPIRATION_HOURS
            )

        to_encode = {
            "sub": subject,
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "access",
        }

        encoded_jwt = jwt.encode(
            to_encode,
            settings.JWT_SECRET,
            algorithm=settings.JWT_ALGORITHM,
        )

        return encoded_jwt

    @staticmethod
    def create_refresh_token(subject: str) -> str:
        """
        Create a JWT refresh token (longer expiration)
        
        Args:
            subject: Subject (usually user ID as string)
            
        Returns:
            Encoded refresh token
        """
        expire = datetime.now(timezone.utc) + timedelta(days=7)

        to_encode = {
            "sub": subject,
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "refresh",
        }

        encoded_jwt = jwt.encode(
            to_encode,
            settings.JWT_SECRET,
            algorithm=settings.JWT_ALGORITHM,
        )

        return encoded_jwt

    @staticmethod
    def verify_token(token: str, token_type: str = "access") -> Optional[str]:
        """
        Verify and decode a JWT token
        
        Args:
            token: JWT token to verify
            token_type: Expected token type (access or refresh)
            
        Returns:
            Subject (user ID) if valid, None if invalid
        """
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET,
                algorithms=[settings.JWT_ALGORITHM],
            )

            # Verify token type
            if payload.get("type") != token_type:
                return None

            subject: str = payload.get("sub")
            if subject is None:
                return None

            return subject

        except JWTError:
            return None

