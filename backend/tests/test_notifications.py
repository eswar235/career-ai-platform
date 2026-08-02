"""
Notification Tests
"""

import uuid
from datetime import datetime, time

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.models.notification import (
    JobAlert,
    Notification,
    EmailNotification,
    AlertJobMatch,
    NotificationPreferences,
)
from app.services.job_alert_service import JobAlertService
from app.services.notification_service import (
    NotificationService,
    EmailNotificationService,
    NotificationPreferencesService,
)


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def test_user(db_session):
    """Create test user"""
    from app.models.user import User
    user = User(
        email=f"test_{uuid.uuid4()}@example.com",
        password_hash="hashed_password",
        full_name="Test User",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def test_job(db_session):
    """Create test job"""
    from app.models.job import Job
    job = Job(
        title="Software Engineer",
        company_name="Test Company",
        location="San Francisco, CA",
        job_type="Full-time",
        description="Test job description",
        source="test",
        source_url="https://example.com/job",
    )
    db_session.add(job)
    db_session.commit()
    return job


class TestJobAlertService:
    """Job Alert Service Tests"""

    def test_create_alert(self, db_session, test_user):
        """Test creating job alert"""
        alert = JobAlertService.create_or_get_alert(
            db=db_session,
            user_id=test_user.id,
            keywords="Python Django",
            locations=["San Francisco", "New York"],
            job_titles=["Backend Engineer"],
            experience_levels=["Senior"],
            salary_min=100000,
            salary_max=200000,
            min_match_score=70,
            notification_frequency="daily",
        )

        assert alert is not None
        assert alert.user_id == test_user.id
        assert alert.keywords == "Python Django"
        assert alert.min_match_score == 70

    def test_get_alert(self, db_session, test_user):
        """Test retrieving job alert"""
        created = JobAlertService.create_or_get_alert(
            db=db_session,
            user_id=test_user.id,
            keywords="Python",
        )

        retrieved = JobAlertService.get_alert(db_session, test_user.id)

        assert retrieved is not None
        assert retrieved.id == created.id

    def test_update_alert(self, db_session, test_user):
        """Test updating job alert"""
        JobAlertService.create_or_get_alert(
            db=db_session,
            user_id=test_user.id,
            keywords="Python",
        )

        updated = JobAlertService.update_alert(
            db_session,
            test_user.id,
            keywords="Python Django",
            min_match_score=80,
        )

        assert updated.keywords == "Python Django"
        assert updated.min_match_score == 80

    def test_toggle_alert(self, db_session, test_user):
        """Test toggling alert on/off"""
        JobAlertService.create_or_get_alert(
            db=db_session,
            user_id=test_user.id,
            keywords="Python",
        )

        toggled = JobAlertService.toggle_alert(db_session, test_user.id, False)

        assert toggled.is_active == False

    def test_find_matching_jobs(self, db_session, test_user, test_job):
        """Test finding matching jobs"""
        alert = JobAlertService.create_or_get_alert(
            db=db_session,
            user_id=test_user.id,
            keywords="Software",
            locations=["San Francisco", "California"],
        )

        matching_jobs = JobAlertService.find_matching_jobs(db_session, alert)

        assert len(matching_jobs) > 0
        assert test_job in matching_jobs

    def test_record_match(self, db_session, test_user, test_job):
        """Test recording alert-job match"""
        alert = JobAlertService.create_or_get_alert(
            db=db_session,
            user_id=test_user.id,
            keywords="Software",
        )

        match = JobAlertService.record_match(
            db_session,
            alert.id,
            test_job.id,
            match_score=85.5,
        )

        assert match is not None
        assert match.alert_id == alert.id
        assert match.job_id == test_job.id
        assert match.match_score == 85.5

    def test_mark_notification_sent(self, db_session, test_user, test_job):
        """Test marking notification as sent"""
        alert = JobAlertService.create_or_get_alert(
            db=db_session,
            user_id=test_user.id,
        )

        match = JobAlertService.record_match(
            db_session,
            alert.id,
            test_job.id,
            90.0,
        )

        updated = JobAlertService.mark_notification_sent(db_session, match.id)

        assert updated.notification_sent == True

    def test_dismiss_match(self, db_session, test_user, test_job):
        """Test dismissing match"""
        alert = JobAlertService.create_or_get_alert(
            db=db_session,
            user_id=test_user.id,
        )

        match = JobAlertService.record_match(
            db_session,
            alert.id,
            test_job.id,
            85.0,
        )

        dismissed = JobAlertService.dismiss_match(db_session, match.id)

        assert dismissed.user_dismissed == True

    def test_get_unsent_matches(self, db_session, test_user, test_job):
        """Test getting unsent matches"""
        alert = JobAlertService.create_or_get_alert(
            db=db_session,
            user_id=test_user.id,
        )

        JobAlertService.record_match(db_session, alert.id, test_job.id, 80.0)

        unsent = JobAlertService.get_unsent_matches(db_session, alert.id)

        assert len(unsent) == 1
        assert unsent[0].notification_sent == False


class TestNotificationService:
    """Notification Service Tests"""

    def test_create_notification(self, db_session, test_user):
        """Test creating notification"""
        notif = NotificationService.create_notification(
            db=db_session,
            user_id=test_user.id,
            notification_type="job_alert",
            title="New Job Match",
            message="Found a job matching your alert",
        )

        assert notif is not None
        assert notif.user_id == test_user.id
        assert notif.is_read == False

    def test_get_notification(self, db_session, test_user):
        """Test retrieving notification"""
        created = NotificationService.create_notification(
            db=db_session,
            user_id=test_user.id,
            notification_type="job_alert",
            title="Test",
            message="Test message",
        )

        retrieved = NotificationService.get_notification(db_session, created.id)

        assert retrieved is not None
        assert retrieved.id == created.id

    def test_get_user_notifications(self, db_session, test_user):
        """Test retrieving user notifications"""
        for i in range(3):
            NotificationService.create_notification(
                db=db_session,
                user_id=test_user.id,
                notification_type="job_alert",
                title=f"Alert {i}",
                message=f"Message {i}",
            )

        total, notifications = NotificationService.get_user_notifications(
            db_session, test_user.id
        )

        assert total == 3
        assert len(notifications) == 3

    def test_mark_as_read(self, db_session, test_user):
        """Test marking notification as read"""
        notif = NotificationService.create_notification(
            db=db_session,
            user_id=test_user.id,
            notification_type="job_alert",
            title="Test",
            message="Test",
        )

        marked = NotificationService.mark_as_read(db_session, notif.id)

        assert marked.is_read == True
        assert marked.read_at is not None

    def test_mark_all_as_read(self, db_session, test_user):
        """Test marking all as read"""
        for i in range(3):
            NotificationService.create_notification(
                db=db_session,
                user_id=test_user.id,
                notification_type="job_alert",
                title=f"Alert {i}",
                message=f"Message {i}",
            )

        count = NotificationService.mark_all_as_read(db_session, test_user.id)

        assert count == 3

    def test_get_unread_count(self, db_session, test_user):
        """Test getting unread count"""
        NotificationService.create_notification(
            db=db_session,
            user_id=test_user.id,
            notification_type="job_alert",
            title="Test",
            message="Test",
        )

        count = NotificationService.get_unread_count(db_session, test_user.id)

        assert count == 1


class TestEmailNotificationService:
    """Email Notification Service Tests"""

    def test_create_email_notification(self, db_session, test_user):
        """Test creating email notification"""
        email_notif = EmailNotificationService.create_email_notification(
            db=db_session,
            user_id=test_user.id,
            email_address="user@example.com",
            notification_type="job_alert",
            subject="New Job Alert",
            body="We found jobs matching your alert",
        )

        assert email_notif is not None
        assert email_notif.status == "pending"
        assert email_notif.subject == "New Job Alert"

    def test_mark_sent(self, db_session, test_user):
        """Test marking email as sent"""
        email_notif = EmailNotificationService.create_email_notification(
            db=db_session,
            user_id=test_user.id,
            email_address="user@example.com",
            notification_type="job_alert",
            subject="Test",
            body="Test",
        )

        marked = EmailNotificationService.mark_sent(db_session, email_notif.id)

        assert marked.status == "sent"
        assert marked.sent_at is not None

    def test_mark_failed(self, db_session, test_user):
        """Test marking email as failed"""
        email_notif = EmailNotificationService.create_email_notification(
            db=db_session,
            user_id=test_user.id,
            email_address="user@example.com",
            notification_type="job_alert",
            subject="Test",
            body="Test",
        )

        marked = EmailNotificationService.mark_failed(
            db_session,
            email_notif.id,
            "SMTP connection failed",
        )

        assert marked.status == "failed"
        assert "SMTP" in marked.delivery_error


class TestNotificationPreferencesService:
    """Notification Preferences Service Tests"""

    def test_get_or_create_preferences(self, db_session, test_user):
        """Test getting or creating preferences"""
        prefs = NotificationPreferencesService.get_or_create_preferences(
            db_session, test_user.id
        )

        assert prefs is not None
        assert prefs.user_id == test_user.id
        assert prefs.job_alerts_enabled == True

    def test_update_preferences(self, db_session, test_user):
        """Test updating preferences"""
        prefs = NotificationPreferencesService.update_preferences(
            db_session,
            test_user.id,
            job_alerts_enabled=False,
            email_notifications_enabled=False,
        )

        assert prefs.job_alerts_enabled == False
        assert prefs.email_notifications_enabled == False


class TestNotificationAPI:
    """Notification API Endpoint Tests"""

    def test_create_alert_endpoint(self, client, test_user, auth_headers):
        """Test POST /api/notifications/alerts"""
        response = client.post(
            "/api/notifications/alerts",
            json={
                "keywords": "Python Django",
                "locations": ["San Francisco"],
                "min_match_score": 70,
                "notification_frequency": "daily",
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["keywords"] == "Python Django"

    def test_get_alert_endpoint(self, client, test_user, auth_headers, db_session):
        """Test GET /api/notifications/alerts"""
        JobAlertService.create_or_get_alert(
            db=db_session,
            user_id=test_user.id,
            keywords="Python",
        )

        response = client.get(
            "/api/notifications/alerts",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["keywords"] == "Python"

    def test_create_notification_endpoint(self, client, test_user, auth_headers):
        """Test creating notification (via service)"""
        from app.services.notification_service import NotificationService

        db_session = next(app.app.state.db.session())
        notif = NotificationService.create_notification(
            db=db_session,
            user_id=test_user.id,
            notification_type="job_alert",
            title="Test Alert",
            message="Test message",
        )

        assert notif.id is not None

    def test_get_notifications_endpoint(self, client, test_user, auth_headers, db_session):
        """Test GET /api/notifications"""
        for i in range(3):
            NotificationService.create_notification(
                db=db_session,
                user_id=test_user.id,
                notification_type="job_alert",
                title=f"Alert {i}",
                message=f"Message {i}",
            )

        response = client.get(
            "/api/notifications",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total_notifications"] >= 3

    def test_mark_as_read_endpoint(self, client, test_user, auth_headers, db_session):
        """Test PUT /api/notifications/{id}/read"""
        notif = NotificationService.create_notification(
            db=db_session,
            user_id=test_user.id,
            notification_type="job_alert",
            title="Test",
            message="Test",
        )

        response = client.put(
            f"/api/notifications/{notif.id}/read",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_read"] == True

    def test_get_preferences_endpoint(self, client, test_user, auth_headers):
        """Test GET /api/notifications/preferences"""
        response = client.get(
            "/api/notifications/preferences",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == str(test_user.id)

    def test_update_preferences_endpoint(self, client, test_user, auth_headers):
        """Test PUT /api/notifications/preferences"""
        response = client.put(
            "/api/notifications/preferences",
            json={
                "job_alerts_enabled": False,
                "daily_digest_enabled": True,
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["job_alerts_enabled"] == False
        assert data["daily_digest_enabled"] == True
