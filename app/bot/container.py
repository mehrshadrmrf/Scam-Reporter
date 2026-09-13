"""
از آنجا که Handler های Aiogram خارج از چرخه‌ی درخواست FastAPI اجرا می‌شوند،
این ماژول یک Factory ساده برای ساخت Repository/Service ها با یک Session مستقل فراهم می‌کند.
"""
from contextlib import asynccontextmanager
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import db_session_context
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
from app.services.trust_score_service import TrustScoreService


@dataclass
class BotServices:
    session: AsyncSession
    users: UserRepository
    reports: ReportRepository
    cases: CaseRepository
    evidence: EvidenceRepository
    audit: AuditLogRepository
    notifications: NotificationRepository
    report_service: ReportService
    case_service: CaseService
    search_service: SearchService
    trust_score_service: TrustScoreService


@asynccontextmanager
async def bot_services():
    async with db_session_context() as session:
        users = UserRepository(session)
        reports = ReportRepository(session)
        cases = CaseRepository(session)
        evidence = EvidenceRepository(session)
        audit = AuditLogRepository(session)
        notifications = NotificationRepository(session)

        trust_score_service = TrustScoreService(users)
        duplicate_service = DuplicateDetectionService(reports)
        notification_service = NotificationService(notifications, reports)

        report_service = ReportService(reports, cases, users, duplicate_service, trust_score_service)
        case_service = CaseService(cases, reports, audit, notification_service, trust_score_service)
        search_service = SearchService(cases)

        yield BotServices(
            session=session,
            users=users,
            reports=reports,
            cases=cases,
            evidence=evidence,
            audit=audit,
            notifications=notifications,
            report_service=report_service,
            case_service=case_service,
            search_service=search_service,
            trust_score_service=trust_score_service,
        )
