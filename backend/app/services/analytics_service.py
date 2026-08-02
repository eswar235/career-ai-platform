"""
Analytics Service - Dashboard and reporting
"""

import logging
import uuid
from typing import List, Tuple, Optional, Dict
from datetime import datetime, date, timedelta
from statistics import mean

from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc, or_

from app.models.analytics import (
    ApplicationStatistics,
    ApplicationTrends,
    RoleAnalytics,
    CompanyAnalytics,
    SourceAnalytics,
    JobAnalytics,
)
from app.models.application import JobApplication
from app.models.job import Job

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Analytics and reporting service"""

    @staticmethod
    def get_or_create_statistics(db: Session, user_id: uuid.UUID) -> ApplicationStatistics:
        """Get or create application statistics"""
        try:
            stats = db.query(ApplicationStatistics).filter(
                ApplicationStatistics.user_id == user_id
            ).first()

            if not stats:
                stats = ApplicationStatistics(
                    user_id=user_id,
                    total_submitted=0,
                    total_pending=0,
                    total_rejected=0,
                    total_interviews=0,
                    total_offers=0,
                )
                db.add(stats)
                db.commit()
                db.refresh(stats)

            return stats

        except Exception as e:
            logger.error(f"Error getting/creating statistics: {str(e)}")
            db.rollback()
            raise

    @staticmethod
    def update_statistics(db: Session, user_id: uuid.UUID) -> ApplicationStatistics:
        """Update statistics by calculating from applications"""
        try:
            stats = AnalyticsService.get_or_create_statistics(db, user_id)

            # Get all applications for user
            applications = db.query(JobApplication).filter(
                JobApplication.user_id == user_id
            ).all()

            # Calculate status counts
            stats.total_submitted = len(applications)
            stats.total_pending = sum(1 for a in applications if a.status == "applied")
            stats.total_rejected = sum(1 for a in applications if a.status == "rejected")
            stats.total_interviews = sum(1 for a in applications if a.status in ["interview_scheduled", "interview_completed"])
            stats.total_offers = sum(1 for a in applications if a.status in ["offer_received", "accepted"])

            # Calculate response rate (applications with any update)
            reviewed = stats.total_rejected + stats.total_interviews + stats.total_offers
            if stats.total_submitted > 0:
                stats.response_rate = (reviewed / stats.total_submitted) * 100
                stats.success_rate = (stats.total_offers / stats.total_submitted) * 100

            # Calculate average response time
            response_times = []
            for app in applications:
                if app.updated_at and app.applied_date:
                    delta = (app.updated_at.date() - app.applied_date.date()).days
                    if delta > 0:
                        response_times.append(delta)

            if response_times:
                stats.average_response_time_days = mean(response_times)

            stats.last_updated = datetime.utcnow()
            db.commit()
            db.refresh(stats)
            logger.info(f"Statistics updated for user {user_id}")
            return stats

        except Exception as e:
            logger.error(f"Error updating statistics: {str(e)}")
            db.rollback()
            raise

    @staticmethod
    def get_statistics(db: Session, user_id: uuid.UUID) -> Optional[ApplicationStatistics]:
        """Get user statistics"""
        try:
            return db.query(ApplicationStatistics).filter(
                ApplicationStatistics.user_id == user_id
            ).first()
        except Exception as e:
            logger.error(f"Error retrieving statistics: {str(e)}")
            raise

    @staticmethod
    def record_daily_trend(
        db: Session,
        user_id: uuid.UUID,
        trend_date: Optional[date] = None,
    ) -> ApplicationTrends:
        """Record daily application trend"""
        try:
            if not trend_date:
                trend_date = date.today()

            trend = db.query(ApplicationTrends).filter(
                and_(
                    ApplicationTrends.user_id == user_id,
                    ApplicationTrends.date == trend_date,
                )
            ).first()

            if trend:
                return trend

            # Get applications for the day
            applications = db.query(JobApplication).filter(
                and_(
                    JobApplication.user_id == user_id,
                    func.date(JobApplication.applied_date) == trend_date,
                )
            ).all()

            trend = ApplicationTrends(
                user_id=user_id,
                date=trend_date,
                applications_submitted=len(applications),
                applications_reviewed=sum(1 for a in applications if a.status != "applied"),
                interviews_scheduled=sum(1 for a in applications if a.status in ["interview_scheduled", "interview_completed"]),
                rejections_received=sum(1 for a in applications if a.status == "rejected"),
                offers_received=sum(1 for a in applications if a.status in ["offer_received", "accepted"]),
            )
            db.add(trend)
            db.commit()
            db.refresh(trend)
            logger.info(f"Daily trend recorded for user {user_id} on {trend_date}")
            return trend

        except Exception as e:
            logger.error(f"Error recording daily trend: {str(e)}")
            db.rollback()
            raise

    @staticmethod
    def get_trends(
        db: Session,
        user_id: uuid.UUID,
        days: int = 30,
    ) -> List[ApplicationTrends]:
        """Get application trends"""
        try:
            start_date = date.today() - timedelta(days=days)
            trends = db.query(ApplicationTrends).filter(
                and_(
                    ApplicationTrends.user_id == user_id,
                    ApplicationTrends.date >= start_date,
                )
            ).order_by(ApplicationTrends.date.asc()).all()

            return trends

        except Exception as e:
            logger.error(f"Error retrieving trends: {str(e)}")
            raise

    @staticmethod
    def update_role_analytics(db: Session, user_id: uuid.UUID) -> None:
        """Update role analytics"""
        try:
            # Get all applications grouped by job title
            applications = db.query(JobApplication).join(
                Job, JobApplication.job_id == Job.id
            ).filter(JobApplication.user_id == user_id).all()

            role_groups = {}
            for app in applications:
                title = app.job.title if app.job else "Unknown"
                if title not in role_groups:
                    role_groups[title] = []
                role_groups[title].append(app)

            # Update role analytics
            for title, apps in role_groups.items():
                role = db.query(RoleAnalytics).filter(
                    and_(
                        RoleAnalytics.user_id == user_id,
                        RoleAnalytics.job_title == title,
                    )
                ).first()

                if not role:
                    role = RoleAnalytics(user_id=user_id, job_title=title)
                    db.add(role)

                role.application_count = len(apps)
                role.interview_count = sum(1 for a in apps if a.status in ["interview_scheduled", "interview_completed"])
                role.offer_count = sum(1 for a in apps if a.status in ["offer_received", "accepted"])
                role.rejection_count = sum(1 for a in apps if a.status == "rejected")
                role.last_applied = max((a.applied_date for a in apps), default=None)

                if role.application_count > 0:
                    role.success_rate = (role.offer_count / role.application_count) * 100

            db.commit()
            logger.info(f"Role analytics updated for user {user_id}")

        except Exception as e:
            logger.error(f"Error updating role analytics: {str(e)}")
            db.rollback()
            raise

    @staticmethod
    def get_top_roles(
        db: Session,
        user_id: uuid.UUID,
        limit: int = 5,
    ) -> List[RoleAnalytics]:
        """Get top applied-to roles"""
        try:
            roles = db.query(RoleAnalytics).filter(
                RoleAnalytics.user_id == user_id
            ).order_by(desc(RoleAnalytics.application_count)).limit(limit).all()

            return roles

        except Exception as e:
            logger.error(f"Error retrieving top roles: {str(e)}")
            raise

    @staticmethod
    def update_company_analytics(db: Session, user_id: uuid.UUID) -> None:
        """Update company analytics"""
        try:
            # Get all applications grouped by company
            applications = db.query(JobApplication).join(
                Job, JobApplication.job_id == Job.id
            ).filter(JobApplication.user_id == user_id).all()

            company_groups = {}
            for app in applications:
                company = app.job.company_name if app.job else "Unknown"
                if company not in company_groups:
                    company_groups[company] = []
                company_groups[company].append(app)

            # Update company analytics
            for company, apps in company_groups.items():
                comp = db.query(CompanyAnalytics).filter(
                    and_(
                        CompanyAnalytics.user_id == user_id,
                        CompanyAnalytics.company_name == company,
                    )
                ).first()

                if not comp:
                    comp = CompanyAnalytics(user_id=user_id, company_name=company)
                    db.add(comp)

                comp.application_count = len(apps)
                comp.interview_count = sum(1 for a in apps if a.status in ["interview_scheduled", "interview_completed"])
                comp.offer_count = sum(1 for a in apps if a.status in ["offer_received", "accepted"])
                comp.rejection_count = sum(1 for a in apps if a.status == "rejected")
                comp.last_applied = max((a.applied_date for a in apps), default=None)

                if comp.application_count > 0:
                    comp.success_rate = (comp.offer_count / comp.application_count) * 100

            db.commit()
            logger.info(f"Company analytics updated for user {user_id}")

        except Exception as e:
            logger.error(f"Error updating company analytics: {str(e)}")
            db.rollback()
            raise

    @staticmethod
    def get_top_companies(
        db: Session,
        user_id: uuid.UUID,
        limit: int = 5,
    ) -> List[CompanyAnalytics]:
        """Get top companies applied to"""
        try:
            companies = db.query(CompanyAnalytics).filter(
                CompanyAnalytics.user_id == user_id
            ).order_by(desc(CompanyAnalytics.application_count)).limit(limit).all()

            return companies

        except Exception as e:
            logger.error(f"Error retrieving top companies: {str(e)}")
            raise

    @staticmethod
    def update_source_analytics(db: Session, user_id: uuid.UUID) -> None:
        """Update source analytics"""
        try:
            # Get all applications grouped by source
            applications = db.query(JobApplication).join(
                Job, JobApplication.job_id == Job.id
            ).filter(JobApplication.user_id == user_id).all()

            source_groups = {}
            for app in applications:
                source = app.job.source if app.job else "Unknown"
                if source not in source_groups:
                    source_groups[source] = []
                source_groups[source].append(app)

            # Update source analytics
            for source, apps in source_groups.items():
                src = db.query(SourceAnalytics).filter(
                    and_(
                        SourceAnalytics.user_id == user_id,
                        SourceAnalytics.source_name == source,
                    )
                ).first()

                if not src:
                    src = SourceAnalytics(user_id=user_id, source_name=source)
                    db.add(src)

                src.application_count = len(apps)
                src.interview_count = sum(1 for a in apps if a.status in ["interview_scheduled", "interview_completed"])
                src.offer_count = sum(1 for a in apps if a.status in ["offer_received", "accepted"])
                src.rejection_count = sum(1 for a in apps if a.status == "rejected")

                if src.application_count > 0:
                    src.success_rate = (src.offer_count / src.application_count) * 100

            db.commit()
            logger.info(f"Source analytics updated for user {user_id}")

        except Exception as e:
            logger.error(f"Error updating source analytics: {str(e)}")
            db.rollback()
            raise

    @staticmethod
    def get_source_breakdown(db: Session, user_id: uuid.UUID) -> List[SourceAnalytics]:
        """Get application breakdown by source"""
        try:
            sources = db.query(SourceAnalytics).filter(
                SourceAnalytics.user_id == user_id
            ).order_by(desc(SourceAnalytics.application_count)).all()

            return sources

        except Exception as e:
            logger.error(f"Error retrieving source breakdown: {str(e)}")
            raise

    @staticmethod
    def refresh_all_analytics(db: Session, user_id: uuid.UUID) -> None:
        """Refresh all analytics for user"""
        try:
            AnalyticsService.update_statistics(db, user_id)
            AnalyticsService.update_role_analytics(db, user_id)
            AnalyticsService.update_company_analytics(db, user_id)
            AnalyticsService.update_source_analytics(db, user_id)
            AnalyticsService.record_daily_trend(db, user_id)
            logger.info(f"All analytics refreshed for user {user_id}")

        except Exception as e:
            logger.error(f"Error refreshing all analytics: {str(e)}")
            raise

    @staticmethod
    def get_status_breakdown(db: Session, user_id: uuid.UUID) -> Dict[str, int]:
        """Get breakdown of applications by status"""
        try:
            applications = db.query(JobApplication).filter(
                JobApplication.user_id == user_id
            ).all()

            breakdown = {}
            for app in applications:
                status = app.status or "unknown"
                breakdown[status] = breakdown.get(status, 0) + 1

            return breakdown

        except Exception as e:
            logger.error(f"Error getting status breakdown: {str(e)}")
            raise

    @staticmethod
    def generate_insights(db: Session, user_id: uuid.UUID) -> List[Dict]:
        """Generate insights from analytics"""
        try:
            insights = []
            stats = AnalyticsService.get_statistics(db, user_id)

            if not stats:
                return insights

            # High response rate insight
            if stats.response_rate and stats.response_rate > 50:
                insights.append({
                    "type": "strength",
                    "title": "Strong Response Rate",
                    "description": f"Your applications have a {stats.response_rate:.1f}% response rate, which is above average.",
                    "metric": stats.response_rate,
                })

            # Low success rate warning
            if stats.success_rate and stats.success_rate < 10 and stats.total_submitted > 5:
                insights.append({
                    "type": "warning",
                    "title": "Low Success Rate",
                    "description": "Your offer rate is below 10%. Consider tailoring your applications or expanding your search criteria.",
                    "metric": stats.success_rate,
                })

            # High application volume opportunity
            if stats.total_submitted > 20:
                insights.append({
                    "type": "opportunity",
                    "title": "Consistent Application Activity",
                    "description": f"You've submitted {stats.total_submitted} applications. Focus on quality over quantity.",
                    "metric": stats.total_submitted,
                })

            # Best performing role
            top_roles = AnalyticsService.get_top_roles(db, user_id, 1)
            if top_roles and top_roles[0].success_rate:
                insights.append({
                    "type": "strength",
                    "title": f"Best Performance in {top_roles[0].job_title}",
                    "description": f"{top_roles[0].job_title} has your highest success rate at {top_roles[0].success_rate:.1f}%.",
                    "metric": top_roles[0].success_rate,
                })

            return insights

        except Exception as e:
            logger.error(f"Error generating insights: {str(e)}")
            raise
