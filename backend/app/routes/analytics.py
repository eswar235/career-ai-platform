"""
Analytics and dashboard API routes
"""

import logging
import csv
from io import StringIO
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import func

from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.application import JobApplication
from app.models.job import Job
from app.schemas.analytics import (
    ApplicationStatisticsResponse,
    DashboardResponse,
    DashboardMetrics,
    TrendsResponse,
    TopRolesResponse,
    TopCompaniesResponse,
    SourceBreakdownResponse,
    ApplicationTrendResponse,
    RoleAnalyticsResponse,
    CompanyAnalyticsResponse,
    SourceAnalyticsResponse,
    DetailedBreakdownResponse,
    StatusBreakdownResponse,
    ExportResponse,
    ApplicationExportRecord,
    InsightsResponse,
    ApplicationInsight,
    AnalyticsPeriodRequest,
)
from app.services.analytics_service import AnalyticsService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/dashboard", response_model=DashboardResponse)
def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get analytics dashboard data"""
    try:
        # Update analytics
        AnalyticsService.refresh_all_analytics(db, current_user.id)

        # Get statistics
        stats = AnalyticsService.get_statistics(db, current_user.id)
        if not stats:
            stats = AnalyticsService.get_or_create_statistics(db, current_user.id)

        # Get top data
        top_roles = AnalyticsService.get_top_roles(db, current_user.id, 5)
        top_companies = AnalyticsService.get_top_companies(db, current_user.id, 5)
        sources = AnalyticsService.get_source_breakdown(db, current_user.id)
        trends = AnalyticsService.get_trends(db, current_user.id, days=30)

        # Build response
        metrics = DashboardMetrics(
            total_applications=stats.total_submitted,
            pending_applications=stats.total_pending,
            rejected_applications=stats.total_rejected,
            interview_scheduled=stats.total_interviews,
            offers_received=stats.total_offers,
            response_rate=stats.response_rate,
            success_rate=stats.success_rate,
            average_response_time=stats.average_response_time_days,
        )

        return DashboardResponse(
            metrics=metrics,
            top_roles=[RoleAnalyticsResponse.from_orm(r) for r in top_roles],
            top_companies=[CompanyAnalyticsResponse.from_orm(c) for c in top_companies],
            sources=[SourceAnalyticsResponse.from_orm(s) for s in sources],
            recent_trends=[ApplicationTrendResponse.from_orm(t) for t in trends[-7:]] if trends else None,
            last_updated=stats.last_updated,
        )

    except Exception as e:
        logger.error(f"Error retrieving dashboard: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                          detail="Failed to retrieve dashboard")


@router.get("/statistics", response_model=ApplicationStatisticsResponse)
def get_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get application statistics"""
    try:
        stats = AnalyticsService.update_statistics(db, current_user.id)
        return stats
    except Exception as e:
        logger.error(f"Error retrieving statistics: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                          detail="Failed to retrieve statistics")


@router.get("/trends", response_model=TrendsResponse)
def get_trends(
    period: str = Query("30days", regex="^(30days|90days|all_time)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get application trends"""
    try:
        days = 30 if period == "30days" else 90 if period == "90days" else 365 * 5

        trends = AnalyticsService.get_trends(db, current_user.id, days)

        total = sum(t.applications_submitted for t in trends)
        avg = total / len(trends) if trends else 0
        peak = max(trends, key=lambda t: t.applications_submitted).date if trends else None

        return TrendsResponse(
            period=period,
            trends=[ApplicationTrendResponse.from_orm(t) for t in trends],
            total_applications=total,
            average_per_day=avg,
            peak_day=peak,
        )

    except Exception as e:
        logger.error(f"Error retrieving trends: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                          detail="Failed to retrieve trends")


@router.get("/top-roles", response_model=TopRolesResponse)
def get_top_roles(
    limit: int = Query(5, ge=1, le=10),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get top applied-to roles"""
    try:
        AnalyticsService.update_role_analytics(db, current_user.id)
        roles = AnalyticsService.get_top_roles(db, current_user.id, limit)

        # Get total unique roles
        all_roles = db.query(func.count(func.distinct(Job.title))).join(
            JobApplication, JobApplication.job_id == Job.id
        ).filter(JobApplication.user_id == current_user.id).scalar()

        return TopRolesResponse(
            top_roles=[RoleAnalyticsResponse.from_orm(r) for r in roles],
            total_unique_roles=all_roles or 0,
        )

    except Exception as e:
        logger.error(f"Error retrieving top roles: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                          detail="Failed to retrieve top roles")


@router.get("/top-companies", response_model=TopCompaniesResponse)
def get_top_companies(
    limit: int = Query(5, ge=1, le=10),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get top companies applied to"""
    try:
        AnalyticsService.update_company_analytics(db, current_user.id)
        companies = AnalyticsService.get_top_companies(db, current_user.id, limit)

        # Get total unique companies
        all_companies = db.query(func.count(func.distinct(Job.company_name))).join(
            JobApplication, JobApplication.job_id == Job.id
        ).filter(JobApplication.user_id == current_user.id).scalar()

        return TopCompaniesResponse(
            top_companies=[CompanyAnalyticsResponse.from_orm(c) for c in companies],
            total_unique_companies=all_companies or 0,
        )

    except Exception as e:
        logger.error(f"Error retrieving top companies: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                          detail="Failed to retrieve top companies")


@router.get("/sources", response_model=SourceBreakdownResponse)
def get_source_breakdown(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get application breakdown by source"""
    try:
        AnalyticsService.update_source_analytics(db, current_user.id)
        sources = AnalyticsService.get_source_breakdown(db, current_user.id)

        return SourceBreakdownResponse(
            sources=[SourceAnalyticsResponse.from_orm(s) for s in sources],
            total_sources=len(sources),
        )

    except Exception as e:
        logger.error(f"Error retrieving source breakdown: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                          detail="Failed to retrieve source breakdown")


@router.get("/breakdown", response_model=DetailedBreakdownResponse)
def get_detailed_breakdown(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get detailed breakdown by status, title, company, and source"""
    try:
        applications = db.query(JobApplication).join(
            Job, JobApplication.job_id == Job.id
        ).filter(JobApplication.user_id == current_user.id).all()

        # Build breakdowns
        by_status = {}
        by_title = {}
        by_company = {}
        by_source = {}
        by_experience = {}

        for app in applications:
            status = app.status or "unknown"
            by_status[status] = by_status.get(status, 0) + 1

            if app.job:
                title = app.job.title or "Unknown"
                by_title[title] = by_title.get(title, 0) + 1

                company = app.job.company_name or "Unknown"
                by_company[company] = by_company.get(company, 0) + 1

                source = app.job.source or "Unknown"
                by_source[source] = by_source.get(source, 0) + 1

                exp = app.job.experience_level or "Unknown"
                by_experience[exp] = by_experience.get(exp, 0) + 1

        # Convert to status breakdown format
        total = len(applications)
        status_list = [
            StatusBreakdownResponse(
                status=k,
                count=v,
                percentage=(v / total * 100) if total > 0 else 0,
            )
            for k, v in by_status.items()
        ]

        return DetailedBreakdownResponse(
            by_status=status_list,
            by_title=by_title,
            by_company=by_company,
            by_source=by_source,
            by_experience_level=by_experience,
        )

    except Exception as e:
        logger.error(f"Error retrieving breakdown: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                          detail="Failed to retrieve breakdown")


@router.get("/insights", response_model=InsightsResponse)
def get_insights(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get application insights"""
    try:
        insights_data = AnalyticsService.generate_insights(db, current_user.id)
        insights = [
            ApplicationInsight(
                insight_type=i["type"],
                title=i["title"],
                description=i["description"],
                metric=i.get("metric"),
            )
            for i in insights_data
        ]

        return InsightsResponse(
            insights=insights,
            generated_at=datetime.utcnow(),
        )

    except Exception as e:
        logger.error(f"Error generating insights: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                          detail="Failed to generate insights")


@router.get("/export", response_class=StreamingResponse)
def export_applications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Export applications as CSV"""
    try:
        applications = db.query(JobApplication).join(
            Job, JobApplication.job_id == Job.id
        ).filter(JobApplication.user_id == current_user.id).all()

        # Create CSV
        output = StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow([
            "Job Title",
            "Company",
            "Source",
            "Submission Date",
            "Status",
            "Notes",
        ])

        # Write data
        for app in applications:
            writer.writerow([
                app.job.title if app.job else "Unknown",
                app.job.company_name if app.job else "Unknown",
                app.job.source if app.job else "Unknown",
                app.applied_date.strftime("%Y-%m-%d") if app.applied_date else "",
                app.status or "unknown",
                app.notes or "",
            ])

        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=applications_export.csv"}
        )

    except Exception as e:
        logger.error(f"Error exporting applications: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                          detail="Failed to export applications")
