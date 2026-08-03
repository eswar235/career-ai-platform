"""
Database configuration and session management
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from app.core.config import settings

# Lazy-load database engine to prevent crashes on startup
engine = None
SessionLocal = None
Base = declarative_base()


def get_engine():
    """Get or create database engine"""
    global engine
    if engine is None:
        engine = create_engine(
            settings.DATABASE_URL,
            echo=settings.SQLALCHEMY_ECHO,
            pool_size=settings.DB_POOL_SIZE,
            max_overflow=settings.DB_MAX_OVERFLOW,
            pool_timeout=settings.DB_POOL_TIMEOUT,
            pool_recycle=settings.DB_POOL_RECYCLE,
            pool_pre_ping=True,  # Verify connections before using
        )
    return engine


def get_session_local():
    """Get or create session factory"""
    global SessionLocal
    if SessionLocal is None:
        SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=get_engine(),
        )
    return SessionLocal


def get_db() -> Session:
    """
    Dependency to get database session
    
    Yields:
        Database session
    """
    db = get_session_local()()
    try:
        yield db
    finally:
        db.close()

