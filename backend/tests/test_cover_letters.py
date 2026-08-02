"""
Unit and integration tests for cover letter functionality
"""

import pytest
import uuid
from datetime import datetime

from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from app.main import app
from app.models.cover_letter import CoverLetter, LetterTemplate, LetterExport
from app.models.job import Job
from app.models.user import User
from app.models.profile import UserProfile
from app.services.cover_letter_service import CoverLetterService
from app.services.generation_service import GenerationService
from app.services.template_service import TemplateService
from app.services.export_service import ExportService
from app.schemas.cover_letter import (
    LetterTemplateCreate,
    CoverLetterUpdate,
)

client = TestClient(app)


@pytest.fixture
def sample_job(db: Session, sample_user: User) -> Job:
    """Create a sample job for testing"""
    job = Job(
        id=uuid.uuid4(),
        user_id=sample_user.id,
        title="Software Engineer",
        company="Tech Corp",
        location="San Francisco, CA",
        description="Looking for a skilled software engineer with 5+ years experience",
        job_type="Full-time",
        salary_min=120000,
        salary_max=180000,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


@pytest.fixture
def sample_profile(db: Session, sample_user: User) -> UserProfile:
    """Create a sample user profile"""
    profile = UserProfile(
        user_id=sample_user.id,
        professional_summary="Experienced software engineer passionate about technology",
        target_role="Senior Software Engineer",
        career_goals="Lead engineering teams and drive technical innovation",
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


class TestCoverLetterService:
    """Test cover letter CRUD operations"""

    def test_create_cover_letter(self, db: Session, sample_user: User, sample_job: Job):
        """Test creating a cover letter"""
        content = "Dear Hiring Manager, I am interested in the Software Engineer position..."
        letter = CoverLetterService.create_cover_letter(
            db=db,
            user_id=sample_user.id,
            job_id=sample_job.id,
            content=content,
        )

        assert letter.id is not None
        assert letter.user_id == sample_user.id
        assert letter.job_id == sample_job.id
        assert letter.content == content
        assert letter.version_number == 1
        assert letter.is_draft is True

    def test_create_multiple_versions(self, db: Session, sample_user: User, sample_job: Job):
        """Test creating multiple versions of a cover letter"""
        content1 = "Version 1 content"
        letter1 = CoverLetterService.create_cover_letter(
            db=db,
            user_id=sample_user.id,
            job_id=sample_job.id,
            content=content1,
        )
        assert letter1.version_number == 1

        content2 = "Version 2 content"
        letter2 = CoverLetterService.create_cover_letter(
            db=db,
            user_id=sample_user.id,
            job_id=sample_job.id,
            content=content2,
        )
        assert letter2.version_number == 2

    def test_get_cover_letter(self, db: Session, sample_user: User, sample_job: Job):
        """Test retrieving a cover letter"""
        content = "Test cover letter"
        created_letter = CoverLetterService.create_cover_letter(
            db=db,
            user_id=sample_user.id,
            job_id=sample_job.id,
            content=content,
        )

        retrieved_letter = CoverLetterService.get_cover_letter(db, created_letter.id)
        assert retrieved_letter is not None
        assert retrieved_letter.id == created_letter.id
        assert retrieved_letter.content == content

    def test_get_cover_letter_for_job(self, db: Session, sample_user: User, sample_job: Job):
        """Test retrieving the latest cover letter for a job"""
        content1 = "Version 1"
        CoverLetterService.create_cover_letter(
            db=db,
            user_id=sample_user.id,
            job_id=sample_job.id,
            content=content1,
        )

        content2 = "Version 2"
        letter2 = CoverLetterService.create_cover_letter(
            db=db,
            user_id=sample_user.id,
            job_id=sample_job.id,
            content=content2,
        )

        latest = CoverLetterService.get_cover_letter_for_job(
            db, sample_user.id, sample_job.id
        )
        assert latest.id == letter2.id
        assert latest.version_number == 2

    def test_update_cover_letter(self, db: Session, sample_user: User, sample_job: Job):
        """Test updating a cover letter"""
        content = "Original content"
        letter = CoverLetterService.create_cover_letter(
            db=db,
            user_id=sample_user.id,
            job_id=sample_job.id,
            content=content,
        )

        update_data = CoverLetterUpdate(
            content="Updated content",
            custom_edits="Added more specific examples",
        )
        updated = CoverLetterService.update_cover_letter(db, letter.id, update_data)

        assert updated.content == "Updated content"
        assert updated.custom_edits == "Added more specific examples"

    def test_publish_cover_letter(self, db: Session, sample_user: User, sample_job: Job):
        """Test publishing a cover letter"""
        letter = CoverLetterService.create_cover_letter(
            db=db,
            user_id=sample_user.id,
            job_id=sample_job.id,
            content="Content",
        )
        assert letter.is_draft is True

        published = CoverLetterService.publish_cover_letter(db, letter.id)
        assert published.is_draft is False

    def test_list_cover_letters(self, db: Session, sample_user: User, sample_job: Job):
        """Test listing cover letters"""
        # Create multiple letters
        for i in range(3):
            CoverLetterService.create_cover_letter(
                db=db,
                user_id=sample_user.id,
                job_id=sample_job.id,
                content=f"Letter {i}",
            )

        total, letters = CoverLetterService.list_cover_letters(
            db, sample_user.id, skip=0, limit=10
        )

        assert total >= 3
        assert len(letters) >= 3

    def test_delete_cover_letter(self, db: Session, sample_user: User, sample_job: Job):
        """Test deleting a cover letter"""
        letter = CoverLetterService.create_cover_letter(
            db=db,
            user_id=sample_user.id,
            job_id=sample_job.id,
            content="Content",
        )

        CoverLetterService.delete_cover_letter(db, letter.id)

        retrieved = CoverLetterService.get_cover_letter(db, letter.id)
        assert retrieved is None


class TestTemplateService:
    """Test letter template operations"""

    def test_create_template(self, db: Session, sample_user: User):
        """Test creating a template"""
        template_data = LetterTemplateCreate(
            name="Professional Template",
            content="Dear Hiring Manager, [custom content]",
            is_default=True,
        )

        template = TemplateService.create_template(db, sample_user.id, template_data)

        assert template.id is not None
        assert template.user_id == sample_user.id
        assert template.name == "Professional Template"
        assert template.is_default is True

    def test_get_template(self, db: Session, sample_user: User):
        """Test retrieving a template"""
        template_data = LetterTemplateCreate(
            name="Test Template",
            content="Template content",
        )
        created = TemplateService.create_template(db, sample_user.id, template_data)

        retrieved = TemplateService.get_template(db, created.id)
        assert retrieved is not None
        assert retrieved.id == created.id

    def test_get_default_template(self, db: Session, sample_user: User):
        """Test getting the default template"""
        template_data = LetterTemplateCreate(
            name="Default",
            content="Default template content",
            is_default=True,
        )
        TemplateService.create_template(db, sample_user.id, template_data)

        default = TemplateService.get_default_template(db, sample_user.id)
        assert default is not None
        assert default.is_default is True

    def test_list_templates(self, db: Session, sample_user: User):
        """Test listing templates"""
        for i in range(3):
            template_data = LetterTemplateCreate(
                name=f"Template {i}",
                content=f"Content {i}",
            )
            TemplateService.create_template(db, sample_user.id, template_data)

        total, templates = TemplateService.list_templates(db, sample_user.id)

        assert total >= 3
        assert len(templates) >= 3

    def test_delete_template(self, db: Session, sample_user: User):
        """Test deleting a template"""
        template_data = LetterTemplateCreate(
            name="Delete Me",
            content="Content",
        )
        template = TemplateService.create_template(db, sample_user.id, template_data)

        TemplateService.delete_template(db, template.id, sample_user.id)

        retrieved = TemplateService.get_template(db, template.id)
        assert retrieved is None


class TestExportService:
    """Test cover letter export functionality"""

    def test_export_as_text(self, db: Session, sample_user: User, sample_job: Job):
        """Test exporting as text"""
        letter = CoverLetterService.create_cover_letter(
            db=db,
            user_id=sample_user.id,
            job_id=sample_job.id,
            content="Test content",
        )

        export = ExportService.export_as_text(db, letter.id)

        assert export.id is not None
        assert export.cover_letter_id == letter.id
        assert export.format == "txt"
        assert export.file_url is not None

    def test_export_as_pdf(self, db: Session, sample_user: User, sample_job: Job):
        """Test exporting as PDF"""
        letter = CoverLetterService.create_cover_letter(
            db=db,
            user_id=sample_user.id,
            job_id=sample_job.id,
            content="Test content",
        )

        export = ExportService.export_as_pdf(db, letter.id)

        assert export.format == "pdf"
        assert export.file_url is not None

    def test_export_as_docx(self, db: Session, sample_user: User, sample_job: Job):
        """Test exporting as DOCX"""
        letter = CoverLetterService.create_cover_letter(
            db=db,
            user_id=sample_user.id,
            job_id=sample_job.id,
            content="Test content",
        )

        export = ExportService.export_as_docx(db, letter.id)

        assert export.format == "docx"
        assert export.file_url is not None

    def test_get_exports(self, db: Session, sample_user: User, sample_job: Job):
        """Test retrieving all exports"""
        letter = CoverLetterService.create_cover_letter(
            db=db,
            user_id=sample_user.id,
            job_id=sample_job.id,
            content="Test content",
        )

        ExportService.export_as_text(db, letter.id)
        ExportService.export_as_pdf(db, letter.id)

        exports = ExportService.get_exports(db, letter.id)

        assert len(exports) >= 2
        formats = [e.format for e in exports]
        assert "txt" in formats
        assert "pdf" in formats


class TestCoverLetterAPI:
    """Test cover letter API endpoints"""

    def test_generate_cover_letter(
        self,
        db: Session,
        sample_user: User,
        sample_job: Job,
        sample_profile: UserProfile,
        auth_token: str,
    ):
        """Test generating a cover letter via API"""
        response = client.post(
            "/api/cover-letters/generate",
            json={
                "job_id": str(sample_job.id),
                "use_profile": True,
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "content" in data
        assert data["version_number"] == 1

    def test_list_cover_letters_api(
        self,
        db: Session,
        sample_user: User,
        sample_job: Job,
        auth_token: str,
    ):
        """Test listing cover letters via API"""
        # Create a letter
        CoverLetterService.create_cover_letter(
            db=db,
            user_id=sample_user.id,
            job_id=sample_job.id,
            content="Test letter",
        )

        response = client.get(
            "/api/cover-letters",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_get_cover_letter_api(
        self,
        db: Session,
        sample_user: User,
        sample_job: Job,
        auth_token: str,
    ):
        """Test retrieving a cover letter via API"""
        letter = CoverLetterService.create_cover_letter(
            db=db,
            user_id=sample_user.id,
            job_id=sample_job.id,
            content="Test letter",
        )

        response = client.get(
            f"/api/cover-letters/{letter.id}",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(letter.id)
        assert data["content"] == "Test letter"

    def test_update_cover_letter_api(
        self,
        db: Session,
        sample_user: User,
        sample_job: Job,
        auth_token: str,
    ):
        """Test updating a cover letter via API"""
        letter = CoverLetterService.create_cover_letter(
            db=db,
            user_id=sample_user.id,
            job_id=sample_job.id,
            content="Original",
        )

        response = client.put(
            f"/api/cover-letters/{letter.id}",
            json={
                "content": "Updated content",
                "custom_edits": "Made edits",
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["content"] == "Updated content"

    def test_publish_cover_letter_api(
        self,
        db: Session,
        sample_user: User,
        sample_job: Job,
        auth_token: str,
    ):
        """Test publishing a cover letter via API"""
        letter = CoverLetterService.create_cover_letter(
            db=db,
            user_id=sample_user.id,
            job_id=sample_job.id,
            content="Content",
        )

        response = client.post(
            f"/api/cover-letters/{letter.id}/publish",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_draft"] is False

    def test_delete_cover_letter_api(
        self,
        db: Session,
        sample_user: User,
        sample_job: Job,
        auth_token: str,
    ):
        """Test deleting a cover letter via API"""
        letter = CoverLetterService.create_cover_letter(
            db=db,
            user_id=sample_user.id,
            job_id=sample_job.id,
            content="Content",
        )

        response = client.delete(
            f"/api/cover-letters/{letter.id}",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 204

        # Verify it's deleted
        retrieved = CoverLetterService.get_cover_letter(db, letter.id)
        assert retrieved is None

    def test_export_as_pdf_api(
        self,
        db: Session,
        sample_user: User,
        sample_job: Job,
        auth_token: str,
    ):
        """Test exporting as PDF via API"""
        letter = CoverLetterService.create_cover_letter(
            db=db,
            user_id=sample_user.id,
            job_id=sample_job.id,
            content="Content",
        )

        response = client.post(
            f"/api/cover-letters/{letter.id}/export/pdf",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["format"] == "pdf"

    def test_template_crud_api(self, auth_token: str):
        """Test template CRUD operations via API"""
        # Create
        create_response = client.post(
            "/api/cover-letters/templates",
            json={
                "name": "Test Template",
                "content": "Template content",
                "is_default": True,
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert create_response.status_code == 200
        template_id = create_response.json()["id"]

        # List
        list_response = client.get(
            "/api/cover-letters/templates",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert list_response.status_code == 200

        # Get
        get_response = client.get(
            f"/api/cover-letters/templates/{template_id}",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert get_response.status_code == 200

        # Delete
        delete_response = client.delete(
            f"/api/cover-letters/templates/{template_id}",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert delete_response.status_code == 204
