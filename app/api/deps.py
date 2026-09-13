from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.security import decode_access_token
from app.models.enums import UserRole
from app.models.user import User
from app.repositories.audit_notification_repository import AuditLogRepository, NotificationRepository
from app.repositories.case_repository import CaseRepository
from app.repositories.evidence_repository import EvidenceRepository
from app.repositories.report_repository import ReportRepository
from app.repositories.user_repository import UserRepository
from app.services.case_service import CaseService
from app.services.duplicate_detection_service import DuplicateDetectionService
from app.services.notification_service import NotificationService
from app.services.report_service import ReportService
from app.services.search_service import SearchService
from app.services.statistics_service import StatisticsService
from app.services.trust_score_service import TrustScoreService

DbSession = Annotated[AsyncSession, Depends(get_db_session)]


def get_user_repository(session: DbSession) -> UserRepository:
    return UserRepository(session)


def get_report_repository(session: DbSession) -> ReportRepository:
    return ReportRepository(session)


def get_case_repository(session: DbSession) -> CaseRepository:
    return CaseRepository(session)


def get_evidence_repository(session: DbSession) -> EvidenceRepository:
    return EvidenceRepository(session)


def get_audit_repository(session: DbSession) -> AuditLogRepository:
    return AuditLogRepository(session)


def get_notification_repository(session: DbSession) -> NotificationRepository:
    return NotificationRepository(session)


def get_trust_score_service(
    user_repo: Annotated[UserRepository, Depends(get_user_repository)]
) -> TrustScoreService:
    return TrustScoreService(user_repo)


def get_duplicate_service(
    report_repo: Annotated[ReportRepository, Depends(get_report_repository)]
) -> DuplicateDetectionService:
    return DuplicateDetectionService(report_repo)


def get_notification_service(
    notif_repo: Annotated[NotificationRepository, Depends(get_notification_repository)],
    report_repo: Annotated[ReportRepository, Depends(get_report_repository)],
) -> NotificationService:
    return NotificationService(notif_repo, report_repo)


def get_report_service(
    report_repo: Annotated[ReportRepository, Depends(get_report_repository)],
    case_repo: Annotated[CaseRepository, Depends(get_case_repository)],
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    duplicate_service: Annotated[DuplicateDetectionService, Depends(get_duplicate_service)],
    trust_score_service: Annotated[TrustScoreService, Depends(get_trust_score_service)],
) -> ReportService:
    return ReportService(report_repo, case_repo, user_repo, duplicate_service, trust_score_service)


def get_case_service(
    case_repo: Annotated[CaseRepository, Depends(get_case_repository)],
    report_repo: Annotated[ReportRepository, Depends(get_report_repository)],
    audit_repo: Annotated[AuditLogRepository, Depends(get_audit_repository)],
    notification_service: Annotated[NotificationService, Depends(get_notification_service)],
    trust_score_service: Annotated[TrustScoreService, Depends(get_trust_score_service)],
) -> CaseService:
    return CaseService(case_repo, report_repo, audit_repo, notification_service, trust_score_service)


def get_search_service(
    case_repo: Annotated[CaseRepository, Depends(get_case_repository)]
) -> SearchService:
    return SearchService(case_repo)


def get_statistics_service(session: DbSession) -> StatisticsService:
    return StatisticsService(session)


async def get_current_user(
    session: DbSession,
    authorization: Annotated[str | None, Header()] = None,
) -> User:
    """کاربر جاری را از JWT توکن (Authorization: Bearer <token>) استخراج می‌کند."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "توکن احراز هویت ارسال نشده است.")

    token = authorization.removeprefix("Bearer ").strip()
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "توکن نامعتبر یا منقضی‌شده است.")

    user_repo = UserRepository(session)
    user = await user_repo.get_by_id(UUID(payload["sub"]))
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "کاربر یافت نشد.")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_staff(user: CurrentUser) -> User:
    if user.role == UserRole.REPORTER:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "این عملیات مخصوص تیم بررسی است.")
    return user


StaffUser = Annotated[User, Depends(require_staff)]
