"""Pytest configuration and fixtures"""

import os
import uuid
from typing import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy_utils import create_database, database_exists

from app.core.config import settings
from app.core.database import Base, get_db
from app.main import app
from app.models.user import User


# Override database URL for testing
TEST_SQLALCHEMY_DATABASE_URL = (
    "postgresql://career_ai_user:career_ai_pass@localhost/test_career_ai_db"
)

engine = create_engine(
    TEST_SQLALCHEMY_DATABASE_URL,
    connect_args={},
    echo=False,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


@pytest.fixture(scope="session")
def db() -> Generator[Session, None, None]:
    """Create test database and return session"""
    # Create database if it doesn't exist
    if not database_exists(engine.url):
        create_database(engine.url)

    # Create tables
    Base.metadata.create_all(bind=engine)

    # Yield session
    db = TestingSessionLocal()
    yield db
    db.close()

    # Cleanup
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def session(db: Session) -> Generator[Session, None, None]:
    """Reset database before each test"""
    # Clear all tables
    for table in reversed(Base.metadata.sorted_tables):
        db.execute(table.delete())
    db.commit()

    yield db


@pytest.fixture
def client(session: Session):
    """Create test client"""
    def override_get_db() -> Generator[Session, None, None]:
        yield session

    app.dependency_overrides[get_db] = override_get_db

    from fastapi.testclient import TestClient
    return TestClient(app)



@pytest.fixture
def test_user_data():
    """Test user registration data"""
    return {
        "email": "testuser@example.com",
        "password": "TestPassword123!",
        "full_name": "Test User",
    }


@pytest.fixture
def test_user_id(session: Session) -> uuid.UUID:
    """Create a test user and return its ID"""
    from app.core.security import hash_password
    
    user_id = uuid.uuid4()
    user = User(
        id=user_id,
        email="testuser@example.com",
        full_name="Test User",
        password_hash=hash_password("TestPassword123!"),
        is_active=True,
        email_verified=True,
    )
    session.add(user)
    session.commit()
    return user_id


@pytest.fixture
def sample_user(session: Session) -> User:
    """Create a sample user for testing"""
    from app.core.security import hash_password
    
    user = User(
        id=uuid.uuid4(),
        email="sample@example.com",
        full_name="Sample User",
        password_hash=hash_password("SamplePass123!"),
        is_active=True,
        email_verified=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture
def auth_token(client, test_user_data) -> str:
    """Get auth token for test user"""
    # Register user
    response = client.post(
        "/api/auth/register",
        json=test_user_data,
    )
    
    if response.status_code != 201:
        # User already exists, try to login
        response = client.post(
            "/api/auth/login",
            data={
                "username": test_user_data["email"],
                "password": test_user_data["password"],
            },
        )
    
    if response.status_code in [200, 201]:
        data = response.json()
        if "access_token" in data:
            return data["access_token"]
        elif "token" in data:
            return data["token"]
    
    # Fallback: return a dummy token for testing
    return "test-token"
