"""
سرویس اصلی ثبت گزارش - ارکستراتور بین Report، Case، تشخیص تکراری و Trust Score.
این کلاس دقیقاً «موتور بررسی اولیه» و «جلوگیری از گزارش‌های تکراری» سند طراحی را
با ترکیب چند سرویس کوچک‌تر پیاده‌سازی می‌کند (اصل Single Responsibility در هر جزء).
"""
from dataclasses import dataclass
from datetime import date
from typing import Optional
from uuid import UUID

from app.core.exceptions import NotFoundError, UserBannedError, UserRestrictedError, ValidationError
from app.core.logging import get_logger
from app.models.case import Case
from app.models.enums import (
    AccountStatus,
    CaseStatus,
    Priority,
    PublishStatus,
    ReportCategory,
    TrustScoreReason,
)
from app.models.report import Report
from app.repositories.case_repository import CaseRepository
from app.repositories.report_repository import ReportRepository
from app.repositories.user_repository import UserRepository
from app.services.duplicate_detection_service import DuplicateDetectionService
from app.services.pii_masking_service import PIIMaskingService
from app.services.trust_score_service import TrustScoreService

logger = get_logger(__name__)


@dataclass
class SubmitReportCommand:
    """DTO ورودی برای ثبت یک گزارش جدید - دقیقاً منطبق بر فرم PDD."""
    reporter_id: UUID
    category: ReportCategory
    description: str
    subject_name: Optional[str] = None
    subject_username: Optional[str] = None
    subject_profile_link: Optional[str] = None
    subject_channel_link: Optional[str] = None
    subject_group_link: Optional[str] = None
    subject_card_number: Optional[str] = None
    subject_phone_number: Optional[str] = None
    subject_wallet_address: Optional[str] = None
    subject_domain: Optional[str] = None
    damage_amount: Optional[int] = None
    incident_date: Optional[date] = None


class ReportService:
    def __init__(
        self,
        report_repository: ReportRepository,
        case_repository: CaseRepository,
        user_repository: UserRepository,
        duplicate_service: DuplicateDetectionService,
        trust_score_service: TrustScoreService,
    ):
        self._reports = report_repository
        self._cases = case_repository
        self._users = user_repository
        self._duplicate_service = duplicate_service
        self._trust_score = trust_score_service

    async def submit(self, command: SubmitReportCommand) -> Report:
        reporter = await self._users.get_by_id(command.reporter_id)
        if reporter is None:
            raise NotFoundError("User", str(command.reporter_id))
        if reporter.account_status == AccountStatus.BANNED:
            raise UserBannedError()
        if reporter.account_status == AccountStatus.RESTRICTED:
            raise UserRestrictedError()

        self._validate_minimum_fields(command)

        report = Report(
            reporter_id=reporter.id,
            category=command.category,
            description=command.description,
            subject_name=command.subject_name,
            subject_username=self._normalize_username(command.subject_username),
            subject_profile_link=command.subject_profile_link,
            subject_channel_link=command.subject_channel_link,
            subject_group_link=command.subject_group_link,
            subject_card_number=self._normalize_digits(command.subject_card_number),
            subject_phone_number=self._normalize_digits(command.subject_phone_number),
            subject_wallet_address=command.subject_wallet_address,
            subject_domain=command.subject_domain,
            damage_amount=command.damage_amount,
            incident_date=command.incident_date,
        )
        self._reports.add(report)
        await self._reports.flush()

        # موتور بررسی اولیه: تشخیص تکراری و merge خودکار با پرونده موجود
        duplicate_result = await self._duplicate_service.check(report)
        if duplicate_result.is_duplicate and duplicate_result.matched_report and duplicate_result.matched_report.case:
            case = duplicate_result.matched_report.case
            report.is_duplicate = True
            report.duplicate_of_report_id = duplicate_result.matched_report.id
            report.case_id = case.id
            self._merge_into_case(case, report)
            logger.info("report_merged_into_case", report_id=str(report.id), case_number=case.case_number)
        else:
            case = self._create_case_from_report(report)
            self._cases.add(case)
            await self._cases.flush()
            report.case_id = case.id

        reporter.total_reports += 1
        await self._trust_score.apply_score_event(
            reporter.id, TrustScoreReason.VALID_REPORT, related_report_id=str(report.id)
        )

        await self._reports.commit()
        return report

    def _create_case_from_report(self, report: Report) -> Case:
        masked_card = PIIMaskingService.mask_card_number(report.subject_card_number)
        title = report.subject_username or report.subject_name or report.subject_domain or "پرونده بدون عنوان"
        return Case(
            title=f"گزارش {self._category_label(report.category)} - {title}",
            category=report.category,
            priority=self._infer_priority(report),
            status=CaseStatus.PENDING_REVIEW,
            publish_status=PublishStatus.VISIBLE_TO_ADMIN,
            subject_username=report.subject_username,
            subject_profile_link=report.subject_profile_link,
            subject_channel_link=report.subject_channel_link,
            subject_group_link=report.subject_group_link,
            subject_card_number_masked=masked_card,
            subject_phone_number=report.subject_phone_number,
            subject_wallet_address=report.subject_wallet_address,
            subject_domain=report.subject_domain,
            total_reports=1,
            total_damage_amount=report.damage_amount or 0,
            first_incident_date=report.incident_date,
        )

    def _merge_into_case(self, case: Case, report: Report) -> None:
        case.total_reports += 1
        case.total_damage_amount += report.damage_amount or 0
        if report.incident_date and (
            case.first_incident_date is None or report.incident_date < case.first_incident_date
        ):
            case.first_incident_date = report.incident_date
        # افزایش گزارش‌های مستقل می‌تواند اولویت پرونده را بالا ببرد
        if case.total_reports >= 3 and case.priority == Priority.MEDIUM:
            case.priority = Priority.HIGH

    @staticmethod
    def _infer_priority(report: Report) -> Priority:
        if report.damage_amount and report.damage_amount > 100_000_000:  # بیش از ۱۰۰ میلیون تومان
            return Priority.HIGH
        return Priority.MEDIUM

    @staticmethod
    def _category_label(category: ReportCategory) -> str:
        labels = {
            ReportCategory.FINANCIAL_FRAUD: "کلاهبرداری مالی",
            ReportCategory.FAKE_PRODUCT: "فروش کالای جعلی",
            ReportCategory.FAKE_COURSE_OR_SERVICE: "دوره/خدمات جعلی",
            ReportCategory.IMPERSONATION: "جعل هویت",
            ReportCategory.PHISHING: "فیشینگ",
            ReportCategory.EXTORTION: "اخاذی",
            ReportCategory.HACKING: "هک",
            ReportCategory.MISLEADING_ADS: "تبلیغات گمراه‌کننده",
            ReportCategory.PONZI_SCHEME: "سرمایه‌گذاری/پانزی",
            ReportCategory.CRYPTOCURRENCY: "ارز دیجیتال",
            ReportCategory.GAMBLING: "شرط‌بندی",
            ReportCategory.OTHER: "سایر",
        }
        return labels.get(category, "سایر")

    @staticmethod
    def _validate_minimum_fields(command: SubmitReportCommand) -> None:
        has_any_identifier = any(
            [
                command.subject_username,
                command.subject_profile_link,
                command.subject_channel_link,
                command.subject_group_link,
                command.subject_card_number,
                command.subject_phone_number,
                command.subject_wallet_address,
                command.subject_domain,
            ]
        )
        if not has_any_identifier:
            raise ValidationError("حداقل یکی از شناسه‌های طرف گزارش‌شده باید وارد شود.")
        if not command.description or len(command.description.strip()) < 20:
            raise ValidationError("توضیحات گزارش باید حداقل ۲۰ کاراکتر باشد.")

    @staticmethod
    def _normalize_username(username: Optional[str]) -> Optional[str]:
        if not username:
            return None
        return username.strip().lstrip("@").lower()

    @staticmethod
    def _normalize_digits(value: Optional[str]) -> Optional[str]:
        if not value:
            return None
        return "".join(ch for ch in value if ch.isdigit())
