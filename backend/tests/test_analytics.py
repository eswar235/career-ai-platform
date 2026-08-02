"""
Analytics Tests
"""

import uuid
from datetime import datetime, date, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.models.analytics import (
    ApplicationStatistics,
    ApplicationTrends,
    RoleAnalytics,
    CompanyAnalytics,
    SourceAnalytics,
)
from app.services.analytics_service import AnalyticsService


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
def test_jobs(db_session):
    """Create test jobs"""
    from app.models.job import Job
    jobs = []
    for i in range(3):
        job = Job(
            title="Software Engineer" if i < 2 else "Data Scientist",
            company_name="Company A" if i < 2 else "Company B",
            location="San Francisco, CA",
            job_type="Full-time",
            source="LinkedIn" if i % 2 == 0 else "Indeed",
            source_url=f"https://example.com/job/{i}",
        )
        db_session.add(job)
    db_session.commit()
    db_session.refresh_all(jobs)
    return [db_session.query(Job).all()[i] for i in range(min(3, len(db_session.query(Job).all())))]


@pytest.fixture
def test_applications(db_session, test_user, test_jobs):
    """Create test applications"""
    from app.models.application import JobApplication
    applications = []
    statuses = ["applied", "rejected", "interview_scheduled", "offer_received"]
    
    for i, job in enumerate(test_jobs):
        app = JobApplication(
            user_id=test_user.id,
            job_id=job.id,
            status=statuses[i % len(statuses)],
            applied_date=datetime.utcnow().date() - timedelta(days=i*5),
        )
        db_session.add(app)
    db_session.commit()
    return db_session.query(JobApplication).filter(
        JobApplication.user_id == test_user.id
    ).all()


class TestAnalyticsService:
    """Analytics Service Tests"""

    def test_get_or_create_statistics(self, db_session, test_user):
        """Test getting or creating statistics"""
        stats = AnalyticsService.get_or_create_statistics(db_session, test_user.id)

        assert stats is not None
        assert stats.user_id == test_user.id
        assert stats.total_submitted == 0

    def test_update_statistics(self, db_session, test_user, test_applications):
        """Test updating statistics"""
        stats = AnalyticsService.update_statistics(db_session, test_user.id)

        assert stats.total_submitted == len(test_applications)
        assert stats.total_rejected >= 0
        assert stats.total_interviews >= 0

    def test_get_statistics(self, db_session, test_user):
        """Test retrieving statistics"""
        AnalyticsService.get_or_create_statistics(db_session, test_user.id)
        stats = AnalyticsService.get_statistics(db_session, test_user.id)

        assert stats is not None
        assert stats.user_id == test_user.id

    def test_record_daily_trend(self, db_session, test_user, test_applications):
        """Test recording daily trend"""
        trend_date = date.today()
        trend = AnalyticsService.record_daily_trend(db_session, test_user.id, trend_date)

        assert trend is not None
        assert trend.user_id == test_user.id
        assert trend.date == trend_date

    def test_get_trends(self, db_session, test_user, test_applications):
        """Test retrieving trends"""
        AnalyticsService.record_daily_trend(db_session, test_user.id)
        trends = AnalyticsService.get_trends(db_session, test_user.id, days=30)

        assert len(trends) > 0

    def test_update_role_analytics(self, db_session, test_user, test_applications):
        """Test updating role analytics"""
        AnalyticsService.update_role_analytics(db_session, test_user.id)
        roles = db_session.query(RoleAnalytics).filter(
            RoleAnalytics.user_id == test_user.id
        ).all()

        assert len(roles) > 0

    def test_get_top_roles(self, db_session, test_user, test_applications):
        """Test getting top roles"""
        AnalyticsService.update_role_analytics(db_session, test_user.id)
        roles = AnalyticsService.get_top_roles(db_session, test_user.id, limit=5)

        assert len(roles) > 0

    def test_update_company_analytics(self, db_session, test_user, test_applications):
        """Test updating company analytics"""
        AnalyticsService.update_company_analytics(db_session, test_user.id)
        companies = db_session.query(CompanyAnalytics).filter(
            CompanyAnalytics.user_id == test_user.id
        ).all()

        assert len(companies) > 0

    def test_get_top_companies(self, db_session, test_user, test_applications):
        """Test getting top companies"""
        AnalyticsService.update_company_analytics(db_session, test_user.id)
        companies = AnalyticsService.get_top_companies(db_session, test_user.id, limit=5)

        assert len(companies) > 0

    def test_update_source_analytics(self, db_session, test_user, test_applications):
        """Test updating source analytics"""
        AnalyticsService.update_source_analytics(db_session, test_user.id)
        sources = db_session.query(SourceAnalytics).filter(
            SourceAnalytics.user_id == test_user.id
        ).all()

        assert len(sources) > 0

    def test_get_source_breakdown(self, db_session, test_user, test_applications):
        """Test getting source breakdown"""
        AnalyticsService.update_source_analytics(db_session, test_user.id)
        sources = AnalyticsService.get_source_breakdown(db_session, test_user.id)

        assert len(sources) > 0

    def test_refresh_all_analytics(self, db_session, test_user, test_applications):
        """Test refreshing all analytics"""
        AnalyticsService.refresh_all_analytics(db_session, test_user.id)

        stats = AnalyticsService.get_statistics(db_session, test_user.id)
        assert stats is not None

    def test_get_status_breakdown(self, db_session, test_user, test_applications):
        """Test getting status breakdown"""
        breakdown = AnalyticsService.get_status_breakdown(db_session, test_user.id)

        assert len(breakdown) > 0
        assert sum(breakdown.values()) == len(test_applications)

    def test_generate_insights(self, db_session, test_user, test_applications):
        """Test generating insights"""
        AnalyticsService.update_statistics(db_session, test_user.id)
        insights = AnalyticsService.generate_insights(db_session, test_user.id)

        assert isinstance(insights, list)


class TestAnalyticsAPI:
    """Analytics API Endpoint Tests"""

    def test_dashboard_endpoint(self, client, test_user, auth_headers, db_session, test_applications):
        """Test GET /api/analytics/dashboard"""
        response = client.get(
            "/api/analytics/dashboard",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "metrics" in data
        assert "top_roles" in data
        assert "top_companies" in data

    def test_statistics_endpoint(self, client, test_user, auth_headers, db_session, test_applications):
        """Test GET /api/analytics/statistics"""
        response = client.get(
            "/api/analytics/statistics",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total_submitted"] >= 0

    def test_trends_endpoint(self, client, test_user, auth_headers, db_session, test_applications):
        """Test GET /api/analytics/trends"""
        response = client.get(
            "/api/analytics/trends?period=30days",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["period"] == "30days"
        assert "trends" in data

    def test_top_roles_endpoint(self, client, test_user, auth_headers, db_session, test_applications):
        """Test GET /api/analytics/top-roles"""
        response = client.get(
            "/api/analytics/top-roles",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "top_roles" in data

    def test_top_companies_endpoint(self, client, test_user, auth_headers, db_session, test_applications):
        """Test GET /api/analytics/top-companies"""
        response = client.get(
            "/api/analytics/top-companies",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "top_companies" in data

    def test_sources_endpoint(self, client, test_user, auth_headers, db_session, test_applications):
        """Test GET /api/analytics/sources"""
        response = client.get(
            "/api/analytics/sources",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "sources" in data

    def test_breakdown_endpoint(self, client, test_user, auth_headers, db_session, test_applications):
        """Test GET /api/analytics/breakdown"""
        response = client.get(
            "/api/analytics/breakdown",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "by_status" in data
        assert "by_title" in data

    def test_insights_endpoint(self, client, test_user, auth_headers, db_session, test_applications):
        """Test GET /api/analytics/insights"""
        response = client.get(
            "/api/analytics/insights",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "insights" in data

    def test_export_endpoint(self, client, test_user, auth_headers, db_session, test_applications):
        """Test GET /api/analytics/export"""
        response = client.get(
            "/api/analytics/export",
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"
