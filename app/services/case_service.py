"""
سرویس گردش‌کار بررسی پرونده (State Machine).
تمام انتقال‌های وضعیت از اینجا عبور می‌کنند تا:
  ۱. هیچ انتقال غیرمجازی (طبق CaseStatus.allowed_transitions) رخ ندهد.
  ۲. هر تغییر در ReviewHistory برای شفافیت ثبت شود.
  ۳. قانون «حداقل گزارش‌دهنده مستقل برای انتشار» رعایت شود.
"""
from uuid import UUID

from app.core.config import settings
from app.core.exceptions import InvalidStateTransitionError, NotFoundError, PermissionDeniedError
from app.core.logging import get_logger
from app.models.case import Case
from app.models.enums import AuditAction, CaseStatus, PublishStatus, TrustScoreReason, UserRole
from app.models.review_history import ReviewHistory
from app.models.user import User
from app.repositories.audit_notification_repository import AuditLogRepository, NotificationRepository
from app.repositories.case_repository import CaseRepository
from app.repositories.report_repository import ReportRepository
from app.services.notification_service import NotificationService
from app.services.trust_score_service import TrustScoreService

logger = get_logger(__name__)

_REVIEWER_ROLES = {UserRole.REVIEWER, UserRole.MODERATOR, UserRole.ADMIN, UserRole.SUPER_ADMIN}


class CaseService:
    def __init__(
        self,
        case_repository: CaseRepository,
        report_repository: ReportRepository,
        audit_repository: AuditLogRepository,
        notification_service: NotificationService,
        trust_score_service: TrustScoreService,
    ):
        self._cases = case_repository
        self._reports = report_repository
        self._audit = audit_repository
        self._notifications = notification_service
        self._trust_score = trust_score_service

    async def _transition(
        self, case: Case, target_status: CaseStatus, reviewer: User, note: str | None = None
    ) -> Case:
        if reviewer.role not in _REVIEWER_ROLES:
            raise PermissionDeniedError("فقط اعضای تیم بررسی مجاز به تغییر وضعیت پرونده هستند.")
        if not case.can_transition_to(target_status):
            raise InvalidStateTransitionError(case.status.value, target_status.value)

        history = ReviewHistory(
            case_id=case.id, reviewer_id=reviewer.id, from_status=case.status, to_status=target_status, note=note
        )
        case.status = target_status
        self._cases.add(history)
        await self._cases.flush()
        return case

    async def start_review(self, case_id: UUID, reviewer: User) -> Case:
        case = await self._get_case_or_raise(case_id)
        case = await self._transition(case, CaseStatus.UNDER_REVIEW, reviewer)
        await self._log(reviewer, AuditAction.EDIT, case)
        await self._cases.commit()
        return case

    async def request_more_evidence(self, case_id: UUID, reviewer: User, note: str) -> Case:
        case = await self._get_case_or_raise(case_id)
        case = await self._transition(case, CaseStatus.NEEDS_MORE_EVIDENCE, reviewer, note)
        await self._log(reviewer, AuditAction.REQUEST_EVIDENCE, case, note)
        await self._notify_followers(case, "درخواست مدارک بیشتر", note)
        await self._cases.commit()
        return case

    async def approve(self, case_id: UUID, reviewer: User, note: str | None = None) -> Case:
        case = await self._get_case_or_raise(case_id)
        case = await self._transition(case, CaseStatus.APPROVED, reviewer, note)

        # پاداش اعتبار برای همه گزارش‌دهندگان این پرونده
        for report in await self._reports.list_by_case(case.id):
            await self._trust_score.apply_score_event(
                report.reporter_id, TrustScoreReason.VALID_REPORT, related_report_id=str(report.id)
            )

        await self._log(reviewer, AuditAction.APPROVE, case, note)
        await self._cases.commit()
        return case

    async def reject(self, case_id: UUID, reviewer: User, note: str) -> Case:
        case = await self._get_case_or_raise(case_id)
        case = await self._transition(case, CaseStatus.REJECTED, reviewer, note)
        case.publish_status = PublishStatus.HIDDEN

        for report in await self._reports.list_by_case(case.id):
            await self._trust_score.apply_score_event(
                report.reporter_id, TrustScoreReason.FALSE_REPORT, related_report_id=str(report.id)
            )

        await self._log(reviewer, AuditAction.REJECT, case, note)
        await self._notify_followers(case, "پرونده رد شد", note)
        await self._cases.commit()
        return case

    async def publish(self, case_id: UUID, reviewer: User) -> Case:
        """
        انتشار عمومی پرونده - فقط در صورتی مجاز است که:
          - پرونده در وضعیت APPROVED باشد،
          - و حداقل تعداد گزارش‌دهنده مستقل (طبق تنظیمات) داشته باشد
            (جلوگیری از سوءاستفاده انتقام‌جویانه با یک گزارش تنها).
        """
        case = await self._get_case_or_raise(case_id)
        if reviewer.role not in {UserRole.MODERATOR, UserRole.ADMIN, UserRole.SUPER_ADMIN}:
            raise PermissionDeniedError("فقط مدیران مجاز به انتشار عمومی پرونده هستند.")
        if case.status != CaseStatus.APPROVED:
            raise InvalidStateTransitionError(case.status.value, "published")
        if case.total_reports < settings.min_independent_reporters_to_publish:
            raise PermissionDeniedError(
                f"برای انتشار عمومی این پرونده حداقل {settings.min_independent_reporters_to_publish} "
                "گزارش‌دهنده مستقل لازم است."
            )

        case.publish_status = PublishStatus.PUBLISHED
        await self._log(reviewer, AuditAction.PUBLISH, case)
        await self._notify_followers(case, "پرونده منتشر شد", "این پرونده اکنون به‌صورت عمومی قابل مشاهده است.")
        await self._cases.commit()
        return case

    async def hide(self, case_id: UUID, reviewer: User, note: str) -> Case:
        case = await self._get_case_or_raise(case_id)
        case.publish_status = PublishStatus.HIDDEN
        await self._log(reviewer, AuditAction.EDIT, case, note)
        await self._cases.commit()
        return case

    async def _get_case_or_raise(self, case_id: UUID) -> Case:
        case = await self._cases.get_by_id(case_id)
        if case is None:
            raise NotFoundError("Case", str(case_id))
        return case

    async def _log(self, actor: User, action: AuditAction, case: Case, details: str | None = None) -> None:
        from app.models.audit_log import AuditLog

        self._audit.add(
            AuditLog(actor_id=actor.id, action=action, entity_type="case", entity_id=case.case_number, details=details)
        )
        logger.info("case_audit", case_number=case.case_number, action=action.value, actor=str(actor.id))

    async def _notify_followers(self, case: Case, title: str, body: str | None) -> None:
        await self._notifications.notify_case_followers(case, title, body or "")
