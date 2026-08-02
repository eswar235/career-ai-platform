"""
Tests for resume upload and management endpoints
"""

import io
import pytest
from fastapi.testclient import TestClient
from uuid import uuid4

from app.main import app


@pytest.fixture
def test_client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def auth_headers(test_client, test_user_data):
    """Get authentication headers for test user"""
    # Register user
    response = test_client.post(
        "/api/auth/register",
        json=test_user_data,
    )
    assert response.status_code == 201

    # Login
    login_response = test_client.post(
        "/api/auth/login",
        json={
            "email": test_user_data["email"],
            "password": test_user_data["password"],
        },
    )
    assert login_response.status_code == 200

    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_pdf():
    """Create a sample PDF file for testing"""
    # Minimal PDF content
    pdf_content = (
        b"%PDF-1.4\n"
        b"1 0 obj\n"
        b"<< /Type /Catalog /Pages 2 0 R >>\n"
        b"endobj\n"
        b"2 0 obj\n"
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>\n"
        b"endobj\n"
        b"3 0 obj\n"
        b"<< /Type /Page /Parent 2 0 R /Resources << >> /MediaBox [0 0 612 792] /Contents 4 0 R >>\n"
        b"endobj\n"
        b"4 0 obj\n"
        b"<< >>\n"
        b"stream\n"
        b"BT\n"
        b"/F1 12 Tf\n"
        b"100 700 Td\n"
        b"(Sample Resume) Tj\n"
        b"ET\n"
        b"endstream\n"
        b"endobj\n"
        b"xref\n"
        b"0 5\n"
        b"0000000000 65535 f\n"
        b"0000000009 00000 n\n"
        b"0000000058 00000 n\n"
        b"0000000115 00000 n\n"
        b"0000000214 00000 n\n"
        b"trailer\n"
        b"<< /Size 5 /Root 1 0 R >>\n"
        b"startxref\n"
        b"322\n"
        b"%%EOF\n"
    )
    return io.BytesIO(pdf_content)


class TestResumeUpload:
    """Tests for resume upload endpoint"""

    def test_upload_resume_success(self, test_client, auth_headers, sample_pdf):
        """Test successful resume upload"""
        response = test_client.post(
            "/api/resumes/upload",
            files={"file": ("resume.pdf", sample_pdf, "application/pdf")},
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["original_filename"] == "resume.pdf"
        assert data["file_size"] > 0
        assert data["message"] == "Resume uploaded successfully"

    def test_upload_resume_without_auth(self, test_client, sample_pdf):
        """Test upload without authentication"""
        response = test_client.post(
            "/api/resumes/upload",
            files={"file": ("resume.pdf", sample_pdf, "application/pdf")},
        )

        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"]

    def test_upload_non_pdf_file(self, test_client, auth_headers):
        """Test uploading non-PDF file"""
        response = test_client.post(
            "/api/resumes/upload",
            files={"file": ("resume.txt", io.BytesIO(b"Not a PDF"), "text/plain")},
            headers=auth_headers,
        )

        assert response.status_code == 400
        assert "Only PDF files are allowed" in response.json()["detail"]

    def test_upload_oversized_file(self, test_client, auth_headers):
        """Test uploading file larger than 10MB"""
        # Create 11MB file (over the 10MB limit)
        large_content = b"x" * (11 * 1024 * 1024)
        response = test_client.post(
            "/api/resumes/upload",
            files={"file": ("resume.pdf", io.BytesIO(large_content), "application/pdf")},
            headers=auth_headers,
        )

        assert response.status_code == 413
        assert "exceeds" in response.json()["detail"].lower()


class TestResumeList:
    """Tests for resume listing endpoint"""

    def test_list_resumes_empty(self, test_client, auth_headers):
        """Test listing resumes when none exist"""
        response = test_client.get(
            "/api/resumes/",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert len(data["resumes"]) == 0

    def test_list_resumes_after_upload(self, test_client, auth_headers, sample_pdf):
        """Test listing resumes after upload"""
        # Upload resume
        upload_response = test_client.post(
            "/api/resumes/upload",
            files={"file": ("resume.pdf", sample_pdf, "application/pdf")},
            headers=auth_headers,
        )
        assert upload_response.status_code == 201

        # List resumes
        list_response = test_client.get(
            "/api/resumes/",
            headers=auth_headers,
        )

        assert list_response.status_code == 200
        data = list_response.json()
        assert data["total"] >= 1
        assert len(data["resumes"]) >= 1

    def test_list_resumes_without_auth(self, test_client):
        """Test listing without authentication"""
        response = test_client.get(
            "/api/resumes/",
        )

        assert response.status_code == 401


class TestResumeSetActive:
    """Tests for setting active resume"""

    def test_set_active_resume(self, test_client, auth_headers, sample_pdf):
        """Test setting resume as active"""
        # Upload first resume
        upload1 = test_client.post(
            "/api/resumes/upload",
            files={"file": ("resume1.pdf", sample_pdf, "application/pdf")},
            headers=auth_headers,
        )
        resume1_id = upload1.json()["id"]

        # Upload second resume
        sample_pdf.seek(0)
        upload2 = test_client.post(
            "/api/resumes/upload",
            files={"file": ("resume2.pdf", sample_pdf, "application/pdf")},
            headers=auth_headers,
        )
        resume2_id = upload2.json()["id"]

        # Set first resume as active
        response = test_client.post(
            f"/api/resumes/{resume1_id}/set-active",
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["is_active"] is True

    def test_set_active_nonexistent_resume(self, test_client, auth_headers):
        """Test setting non-existent resume as active"""
        fake_id = str(uuid4())
        response = test_client.post(
            f"/api/resumes/{fake_id}/set-active",
            headers=auth_headers,
        )

        assert response.status_code == 404


class TestResumeDelete:
    """Tests for resume deletion"""

    def test_delete_resume(self, test_client, auth_headers, sample_pdf):
        """Test deleting a resume"""
        # Upload resume
        upload_response = test_client.post(
            "/api/resumes/upload",
            files={"file": ("resume.pdf", sample_pdf, "application/pdf")},
            headers=auth_headers,
        )
        resume_id = upload_response.json()["id"]

        # Delete resume
        delete_response = test_client.delete(
            f"/api/resumes/{resume_id}",
            headers=auth_headers,
        )

        assert delete_response.status_code == 200
        assert "deleted successfully" in delete_response.json()["message"]

        # Verify resume is deleted
        list_response = test_client.get(
            "/api/resumes/",
            headers=auth_headers,
        )
        assert list_response.json()["total"] == 0

    def test_delete_nonexistent_resume(self, test_client, auth_headers):
        """Test deleting non-existent resume"""
        fake_id = str(uuid4())
        response = test_client.delete(
            f"/api/resumes/{fake_id}",
            headers=auth_headers,
        )

        assert response.status_code == 404
