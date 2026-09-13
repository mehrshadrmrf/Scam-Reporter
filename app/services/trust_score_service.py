"""
سرویس مدیریت امتیاز اعتبار (Trust Score) گزارش‌دهندگان.
منطق دقیقاً مطابق جدول PDD پیاده‌سازی شده و کاملاً از UserRepository جدا است
تا قوانین امتیازدهی در یک نقطه مرکزی و قابل تست باشند.
"""
from uuid import UUID

from app.core.config import settings
from app.core.exceptions import NotFoundError
from app.core.logging import get_logger
from app.models.enums import AccountStatus, TrustScoreReason
from app.models.reporter_score_history import ReporterScoreHistory
from app.repositories.user_repository import UserRepository

logger = get_logger(__name__)

_REASON_TO_DELTA = {
    TrustScoreReason.VALID_REPORT: settings.trust_score_valid_report,
    TrustScoreReason.INCOMPLETE_REPORT: settings.trust_score_incomplete_report,
    TrustScoreReason.FALSE_REPORT: settings.trust_score_false_report,
    TrustScoreReason.ABUSE_ATTEMPT: settings.trust_score_abuse_attempt,
}


class TrustScoreService:
    def __init__(self, user_repository: UserRepository):
        self._users = user_repository

    async def apply_score_event(
        self, user_id: UUID, reason: TrustScoreReason, related_report_id: str | None = None
    ) -> ReporterScoreHistory:
        user = await self._users.get_by_id(user_id)
        if user is None:
            raise NotFoundError("User", str(user_id))

        delta = _REASON_TO_DELTA[reason]
        user.trust_score += delta
        self._apply_account_status_rules(user)

        history = ReporterScoreHistory(
            user_id=user.id,
            reason=reason,
            delta=delta,
            resulting_score=user.trust_score,
            related_report_id=related_report_id,
        )
        self._users.add(history)
        await self._users.flush()

        logger.info(
            "trust_score_updated",
            user_id=str(user.id),
            reason=reason.value,
            delta=delta,
            new_score=user.trust_score,
        )
        return history

    @staticmethod
    def _apply_account_status_rules(user) -> None:
        """پس از رسیدن به آستانه مشخص، حساب محدود یا مسدود می‌شود (طبق PDD)."""
        if user.trust_score <= settings.trust_score_ban_threshold:
            user.account_status = AccountStatus.BANNED
        elif user.trust_score <= settings.trust_score_restrict_threshold:
            user.account_status = AccountStatus.RESTRICTED
        else:
            if user.account_status == AccountStatus.RESTRICTED:
                user.account_status = AccountStatus.ACTIVE
