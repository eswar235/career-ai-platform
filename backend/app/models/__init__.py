"""SQLAlchemy ORM Models"""

from app.models.user import User
from app.models.resume import Resume
from app.models.profile import (
    UserProfile,
    ProfileSkill,
    ProfileExperience,
    ProfileEducation,
    ProfileProject,
    ProfileCertification,
    ProfileVersion,
    ProfileCompletionTracking,
)
from app.models.job import (
    Job,
    SavedJob,
    JobSearchHistory,
)
from app.models.matching import (
    ResumeEmbedding,
    JobEmbedding,
    JobMatch,
)
from app.models.optimization import (
    ResumeOptimization,
    TailoredResume,
    OptimizationSuggestion,
)
from app.models.cover_letter import (
    CoverLetter,
    LetterTemplate,
    LetterExport,
)
from app.models.application import (
    JobApplication,
    Interview,
    ApplicationActivity,
    JobOffer,
)
from app.models.automation import (
    AutomationJob,
    AutomationStep,
    AutomationLog,
)
from app.models.interview import (
    InterviewSession,
    InterviewQuestion,
    InterviewAnswer,
    InterviewTip,
    InterviewMetrics,
)
from app.models.notification import (
    JobAlert,
    Notification,
    EmailNotification,
    AlertJobMatch,
    NotificationPreferences,
)
from app.models.analytics import (
    ApplicationStatistics,
    ApplicationTrends,
    JobAnalytics,
    RoleAnalytics,
    CompanyAnalytics,
    SourceAnalytics,
)
from app.models.admin import (
    AuditLog,
    SystemEvent,
    SystemMetric,
    UserSuspension,
)

__all__ = [
    "User",
    "Resume",
    "UserProfile",
    "ProfileSkill",
    "ProfileExperience",
    "ProfileEducation",
    "ProfileProject",
    "ProfileCertification",
    "ProfileVersion",
    "ProfileCompletionTracking",
    "Job",
    "SavedJob",
    "JobSearchHistory",
    "ResumeEmbedding",
    "JobEmbedding",
    "JobMatch",
    "ResumeOptimization",
    "TailoredResume",
    "OptimizationSuggestion",
    "CoverLetter",
    "LetterTemplate",
    "LetterExport",
    "JobApplication",
    "Interview",
    "ApplicationActivity",
    "JobOffer",
    "AutomationJob",
    "AutomationStep",
    "AutomationLog",
    "InterviewSession",
    "InterviewQuestion",
    "InterviewAnswer",
    "InterviewTip",
    "InterviewMetrics",
    "JobAlert",
    "Notification",
    "EmailNotification",
    "AlertJobMatch",
    "NotificationPreferences",
    "ApplicationStatistics",
    "ApplicationTrends",
    "JobAnalytics",
    "RoleAnalytics",
    "CompanyAnalytics",
    "SourceAnalytics",
    "AuditLog",
    "SystemEvent",
    "SystemMetric",
    "UserSuspension",
]
