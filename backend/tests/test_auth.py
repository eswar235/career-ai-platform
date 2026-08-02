"""Tests for authentication endpoints"""

import pytest
from fastapi.testclient import TestClient

from app.schemas.user import UserCreate
from app.services.auth_service import AuthService
from sqlalchemy.orm import Session


class TestUserRegistration:
    """Test user registration endpoint"""

    def test_register_valid_user(self, client: TestClient):
        """Test registering a valid user"""
        user_data = {
            "email": "test@example.com",
            "password": "TestPassword123",
            "full_name": "Test User",
        }

        response = client.post("/api/auth/register", json=user_data)

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["full_name"] == user_data["full_name"]
        assert "id" in data
        assert data["email_verified"] is False
        assert data["is_active"] is True

    def test_register_invalid_email(self, client: TestClient):
        """Test registering with invalid email"""
        user_data = {
            "email": "invalid-email",
            "password": "TestPassword123",
            "full_name": "Test User",
        }

        response = client.post("/api/auth/register", json=user_data)

        assert response.status_code == 422

    def test_register_weak_password(self, client: TestClient):
        """Test registering with weak password"""
        user_data = {
            "email": "test@example.com",
            "password": "weakpass",  # No uppercase, lowercase only
            "full_name": "Test User",
        }

        response = client.post("/api/auth/register", json=user_data)

        assert response.status_code == 422  # Validation error

    def test_register_duplicate_email(self, client: TestClient, session: Session):
        """Test registering with duplicate email"""
        user_data = {
            "email": "test@example.com",
            "password": "TestPassword123",
            "full_name": "Test User",
        }

        # Register first user
        client.post("/api/auth/register", json=user_data)

        # Try to register with same email
        response = client.post("/api/auth/register", json=user_data)

        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()


class TestUserLogin:
    """Test user login endpoint"""

    @pytest.fixture
    def registered_user(self, client: TestClient):
        """Create a registered user for testing"""
        user_data = {
            "email": "test@example.com",
            "password": "TestPassword123",
            "full_name": "Test User",
        }
        client.post("/api/auth/register", json=user_data)
        return user_data

    def test_login_valid_credentials(self, client: TestClient, registered_user):
        """Test login with valid credentials"""
        login_data = {
            "email": registered_user["email"],
            "password": registered_user["password"],
        }

        response = client.post("/api/auth/login", json=login_data)

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] == 3600

    def test_login_invalid_email(self, client: TestClient):
        """Test login with invalid email"""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "TestPassword123",
        }

        response = client.post("/api/auth/login", json=login_data)

        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]

    def test_login_invalid_password(self, client: TestClient, registered_user):
        """Test login with invalid password"""
        login_data = {
            "email": registered_user["email"],
            "password": "WrongPassword123",
        }

        response = client.post("/api/auth/login", json=login_data)

        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]


class TestTokenRefresh:
    """Test token refresh endpoint"""

    @pytest.fixture
    def login_tokens(self, client: TestClient, registered_user):
        """Get tokens from login"""
        login_data = {
            "email": registered_user["email"],
            "password": registered_user["password"],
        }
        response = client.post("/api/auth/login", json=login_data)
        return response.json()

    @pytest.fixture
    def registered_user(self, client: TestClient):
        """Create a registered user"""
        user_data = {
            "email": "test@example.com",
            "password": "TestPassword123",
            "full_name": "Test User",
        }
        client.post("/api/auth/register", json=user_data)
        return user_data

    def test_refresh_token_valid(self, client: TestClient, login_tokens):
        """Test refreshing token with valid refresh token"""
        refresh_data = {"refresh_token": login_tokens["refresh_token"]}

        response = client.post("/api/auth/refresh", json=refresh_data)

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_refresh_token_invalid(self, client: TestClient):
        """Test refreshing with invalid token"""
        refresh_data = {"refresh_token": "invalid_token"}

        response = client.post("/api/auth/refresh", json=refresh_data)

        assert response.status_code == 401
        assert "Invalid refresh token" in response.json()["detail"]


class TestGetCurrentUser:
    """Test get current user endpoint"""

    @pytest.fixture
    def auth_headers(self, client: TestClient, registered_user):
        """Get authorization headers"""
        login_data = {
            "email": registered_user["email"],
            "password": registered_user["password"],
        }
        response = client.post("/api/auth/login", json=login_data)
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    @pytest.fixture
    def registered_user(self, client: TestClient):
        """Create a registered user"""
        user_data = {
            "email": "test@example.com",
            "password": "TestPassword123",
            "full_name": "Test User",
        }
        client.post("/api/auth/register", json=user_data)
        return user_data

    def test_get_current_user_authenticated(self, client: TestClient, auth_headers):
        """Test getting current user when authenticated"""
        response = client.get("/api/auth/me", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["email"] == "test@example.com"
        assert data["full_name"] == "Test User"

    def test_get_current_user_unauthenticated(self, client: TestClient):
        """Test getting current user without authentication"""
        response = client.get("/api/auth/me")

        assert response.status_code == 401

    def test_get_current_user_invalid_token(self, client: TestClient):
        """Test getting current user with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}

        response = client.get("/api/auth/me", headers=headers)

        assert response.status_code == 401


class TestLogout:
    """Test logout endpoint"""

    def test_logout(self, client: TestClient):
        """Test logout endpoint"""
        response = client.post("/api/auth/logout")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "logged out" in data["message"].lower()

