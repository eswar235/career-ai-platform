"""
Integration tests for profile API endpoints
"""

import uuid
from datetime import date
import pytest
from fastapi.testclient import TestClient

from app.core.security import create_access_token


class TestProfileAPI:
    """Tests for profile API endpoints"""

    def test_get_profile_unauthorized(self, client: TestClient):
        """Test getting profile without authentication"""
        response = client.get("/api/profile")
        assert response.status_code == 401

    def test_create_or_get_profile(self, client: TestClient, test_user_id: uuid.UUID, session):
        """Test creating/getting profile"""
        token = create_access_token(str(test_user_id))
        headers = {"Authorization": f"Bearer {token}"}

        response = client.post("/api/profile", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == str(test_user_id)
        assert data["completion_percentage"] == 0

    def test_update_profile(self, client: TestClient, test_user_id: uuid.UUID, session):
        """Test updating profile"""
        token = create_access_token(str(test_user_id))
        headers = {"Authorization": f"Bearer {token}"}

        # Create profile first
        client.post("/api/profile", headers=headers)

        # Update profile
        response = client.patch(
            "/api/profile",
            headers=headers,
            json={
                "first_name": "John",
                "last_name": "Doe",
                "headline": "Software Engineer",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "John"
        assert data["last_name"] == "Doe"

    def test_add_skill(self, client: TestClient, test_user_id: uuid.UUID, session):
        """Test adding a skill"""
        token = create_access_token(str(test_user_id))
        headers = {"Authorization": f"Bearer {token}"}

        # Create profile first
        client.post("/api/profile", headers=headers)

        # Add skill
        response = client.post(
            "/api/profile/skills",
            headers=headers,
            json={
                "skill_name": "Python",
                "proficiency_level": "Advanced",
                "years_of_experience": 5,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["skill_name"] == "Python"

    def test_get_skills(self, client: TestClient, test_user_id: uuid.UUID, session):
        """Test getting skills"""
        token = create_access_token(str(test_user_id))
        headers = {"Authorization": f"Bearer {token}"}

        # Create profile and add skills
        client.post("/api/profile", headers=headers)
        client.post(
            "/api/profile/skills",
            headers=headers,
            json={"skill_name": "Python"},
        )

        # Get skills
        response = client.get("/api/profile/skills", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["skill_name"] == "Python"

    def test_add_experience(self, client: TestClient, test_user_id: uuid.UUID, session):
        """Test adding work experience"""
        token = create_access_token(str(test_user_id))
        headers = {"Authorization": f"Bearer {token}"}

        # Create profile first
        client.post("/api/profile", headers=headers)

        # Add experience
        response = client.post(
            "/api/profile/experiences",
            headers=headers,
            json={
                "job_title": "Software Engineer",
                "company_name": "Tech Corp",
                "start_date": "2020-01-01",
                "currently_working": True,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["job_title"] == "Software Engineer"

    def test_add_education(self, client: TestClient, test_user_id: uuid.UUID, session):
        """Test adding education"""
        token = create_access_token(str(test_user_id))
        headers = {"Authorization": f"Bearer {token}"}

        # Create profile first
        client.post("/api/profile", headers=headers)

        # Add education
        response = client.post(
            "/api/profile/education",
            headers=headers,
            json={
                "institution_name": "MIT",
                "degree": "Bachelor",
                "field_of_study": "Computer Science",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["institution_name"] == "MIT"

    def test_add_project(self, client: TestClient, test_user_id: uuid.UUID, session):
        """Test adding a project"""
        token = create_access_token(str(test_user_id))
        headers = {"Authorization": f"Bearer {token}"}

        # Create profile first
        client.post("/api/profile", headers=headers)

        # Add project
        response = client.post(
            "/api/profile/projects",
            headers=headers,
            json={
                "project_name": "AI Assistant",
                "description": "An AI-powered assistant",
                "skills_used": ["Python", "FastAPI"],
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["project_name"] == "AI Assistant"

    def test_add_certification(self, client: TestClient, test_user_id: uuid.UUID, session):
        """Test adding a certification"""
        token = create_access_token(str(test_user_id))
        headers = {"Authorization": f"Bearer {token}"}

        # Create profile first
        client.post("/api/profile", headers=headers)

        # Add certification
        response = client.post(
            "/api/profile/certifications",
            headers=headers,
            json={
                "certification_name": "AWS Certified Developer",
                "issuing_organization": "Amazon",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["certification_name"] == "AWS Certified Developer"

    def test_delete_skill(self, client: TestClient, test_user_id: uuid.UUID, session):
        """Test deleting a skill"""
        token = create_access_token(str(test_user_id))
        headers = {"Authorization": f"Bearer {token}"}

        # Create profile and add skill
        client.post("/api/profile", headers=headers)
        response = client.post(
            "/api/profile/skills",
            headers=headers,
            json={"skill_name": "Python"},
        )
        skill_id = response.json()["id"]

        # Delete skill
        response = client.delete(
            f"/api/profile/skills/{skill_id}",
            headers=headers,
        )
        assert response.status_code == 204

        # Verify deletion
        response = client.get("/api/profile/skills", headers=headers)
        assert len(response.json()) == 0

    def test_profile_completion_percentage(
        self, client: TestClient, test_user_id: uuid.UUID, session
    ):
        """Test profile completion percentage calculation"""
        token = create_access_token(str(test_user_id))
        headers = {"Authorization": f"Bearer {token}"}

        # Create profile
        client.post("/api/profile", headers=headers)

        # Initial completion should be 0
        response = client.get("/api/profile", headers=headers)
        assert response.json()["completion_percentage"] == 0

        # Update with name
        response = client.patch(
            "/api/profile",
            headers=headers,
            json={"first_name": "John", "last_name": "Doe"},
        )
        assert response.json()["completion_percentage"] > 0

        # Add skill
        client.post(
            "/api/profile/skills",
            headers=headers,
            json={"skill_name": "Python"},
        )

        # Check increased completion
        response = client.get("/api/profile", headers=headers)
        completion1 = response.json()["completion_percentage"]

        # Add experience
        client.post(
            "/api/profile/experiences",
            headers=headers,
            json={
                "job_title": "Engineer",
                "company_name": "Corp",
                "start_date": "2020-01-01",
            },
        )

        # Check further increased completion
        response = client.get("/api/profile", headers=headers)
        completion2 = response.json()["completion_percentage"]
        assert completion2 > completion1
