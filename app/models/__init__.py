"""
همه مدل‌ها اینجا import می‌شوند تا Alembic و Base.metadata
تمام جداول را برای autogenerate/create_all بشناسند.
"""
from app.models.audit_log import AuditLog  # noqa: F401
from app.models.case import Case  # noqa: F401
from app.models.category import Category  # noqa: F401
from app.models.comment import Comment  # noqa: F401
from app.models.evidence import Evidence  # noqa: F401
from app.models.notification import Notification  # noqa: F401
from app.models.report import Report  # noqa: F401
from app.models.reporter_score_history import ReporterScoreHistory  # noqa: F401
from app.models.review_history import ReviewHistory  # noqa: F401
from app.models.tag import Tag, case_tags  # noqa: F401
from app.models.user import User  # noqa: F401

__all__ = [
    "AuditLog",
    "Case",
    "Category",
    "Comment",
    "Evidence",
    "Notification",
    "Report",
    "ReporterScoreHistory",
    "ReviewHistory",
    "Tag",
    "case_tags",
    "User",
]
