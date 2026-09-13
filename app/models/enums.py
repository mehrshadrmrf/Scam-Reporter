"""Enum های دامنه - دقیقاً منطبق بر واژه‌نامه سند طراحی محصول (PDD)."""
import enum


class UserRole(str, enum.Enum):
    REPORTER = "reporter"
    REVIEWER = "reviewer"
    MODERATOR = "moderator"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class AccountStatus(str, enum.Enum):
    ACTIVE = "active"
    RESTRICTED = "restricted"
    BANNED = "banned"


class ReportCategory(str, enum.Enum):
    FINANCIAL_FRAUD = "financial_fraud"
    FAKE_PRODUCT = "fake_product"
    FAKE_COURSE_OR_SERVICE = "fake_course_or_service"
    IMPERSONATION = "impersonation"
    PHISHING = "phishing"
    EXTORTION = "extortion"
    HACKING = "hacking"
    MISLEADING_ADS = "misleading_ads"
    PONZI_SCHEME = "ponzi_scheme"
    CRYPTOCURRENCY = "cryptocurrency"
    GAMBLING = "gambling"
    OTHER = "other"


class CaseStatus(str, enum.Enum):
    REGISTERED = "registered"
    PENDING_REVIEW = "pending_review"
    NEEDS_MORE_EVIDENCE = "needs_more_evidence"
    UNDER_REVIEW = "under_review"
    REJECTED = "rejected"
    APPROVED = "approved"
    ARCHIVED = "archived"

    @classmethod
    def allowed_transitions(cls) -> dict:
        """نقشه انتقال مجاز وضعیت‌ها (State Machine) - منبع حقیقت برای گردش‌کار."""
        return {
            cls.REGISTERED: {cls.PENDING_REVIEW, cls.NEEDS_MORE_EVIDENCE},
            cls.PENDING_REVIEW: {cls.UNDER_REVIEW, cls.NEEDS_MORE_EVIDENCE, cls.REJECTED},
            cls.NEEDS_MORE_EVIDENCE: {cls.PENDING_REVIEW, cls.REJECTED},
            cls.UNDER_REVIEW: {cls.APPROVED, cls.REJECTED, cls.NEEDS_MORE_EVIDENCE},
            cls.APPROVED: {cls.ARCHIVED},
            cls.REJECTED: {cls.ARCHIVED, cls.PENDING_REVIEW},
            cls.ARCHIVED: set(),
        }


class PublishStatus(str, enum.Enum):
    PRIVATE = "private"
    VISIBLE_TO_ADMIN = "visible_to_admin"
    PUBLISHED = "published"
    HIDDEN = "hidden"


class Priority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TrustScoreReason(str, enum.Enum):
    VALID_REPORT = "valid_report"
    INCOMPLETE_REPORT = "incomplete_report"
    FALSE_REPORT = "false_report"
    ABUSE_ATTEMPT = "abuse_attempt"


class AuditAction(str, enum.Enum):
    LOGIN = "login"
    APPROVE = "approve"
    REJECT = "reject"
    EDIT = "edit"
    DELETE = "delete"
    PUBLISH = "publish"
    BAN = "ban"
    RESTORE = "restore"
    MERGE = "merge"
    REQUEST_EVIDENCE = "request_evidence"


class EvidenceType(str, enum.Enum):
    IMAGE = "image"
    VIDEO = "video"
    FILE = "file"
    CHAT_SCREENSHOT = "chat_screenshot"
    OTHER = "other"
