from __future__ import annotations

import random
import string
from datetime import date, datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Date, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import CaseStatus, Priority, PublishStatus, ReportCategory

if TYPE_CHECKING:
    from app.models.comment import Comment
    from app.models.evidence import Evidence
    from app.models.report import Report
    from app.models.review_history import ReviewHistory


def _generate_case_number() -> str:
    """تولید شناسه یکتای انسان‌خوان مانند SR-2026-000184."""
    year = datetime.utcnow().year
    suffix = "".join(random.choices(string.digits, k=6))
    return f"SR-{year}-{suffix}"


class Case(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    پرونده - نتیجه‌ی تجمیع یک یا چند گزارش مشابه درباره‌ی یک فرد/شناسه.
    منطق تغییر وضعیت (state machine) در CaseService پیاده‌سازی می‌شود، نه اینجا،
    تا مدل صرفاً یک Data Holder باقی بماند (Separation of Concerns).
    """
    __tablename__ = "cases"

    case_number: Mapped[str] = mapped_column(
        String(32), unique=True, index=True, nullable=False, default=_generate_case_number
    )
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    category: Mapped[ReportCategory] = mapped_column(Enum(ReportCategory), nullable=False)
    priority: Mapped[Priority] = mapped_column(Enum(Priority), default=Priority.MEDIUM)

    status: Mapped[CaseStatus] = mapped_column(
        Enum(CaseStatus), default=CaseStatus.REGISTERED, nullable=False, index=True
    )
    publish_status: Mapped[PublishStatus] = mapped_column(
        Enum(PublishStatus), default=PublishStatus.PRIVATE, nullable=False, index=True
    )

    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # خلاصه‌سازی خودکار

    # --- شناسه‌های طرف گزارش‌شده (برای جستجو ایندکس می‌شوند) ---
    subject_username: Mapped[Optional[str]] = mapped_column(String(128), index=True, nullable=True)
    subject_profile_link: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    subject_channel_link: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    subject_group_link: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    subject_card_number_masked: Mapped[Optional[str]] = mapped_column(String(32), index=True, nullable=True)
    subject_phone_number: Mapped[Optional[str]] = mapped_column(String(32), index=True, nullable=True)
    subject_wallet_address: Mapped[Optional[str]] = mapped_column(String(128), index=True, nullable=True)
    subject_domain: Mapped[Optional[str]] = mapped_column(String(256), index=True, nullable=True)

    total_reports: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_evidence: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_damage_amount: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    first_incident_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    assigned_reviewer_id: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )

    reports: Mapped[List["Report"]] = relationship(back_populates="case", lazy="selectin")
    evidence: Mapped[List["Evidence"]] = relationship(back_populates="case", lazy="selectin")
    comments: Mapped[List["Comment"]] = relationship(back_populates="case", lazy="selectin")
    review_history: Mapped[List["ReviewHistory"]] = relationship(back_populates="case", lazy="selectin")

    def can_transition_to(self, target: CaseStatus) -> bool:
        return target in CaseStatus.allowed_transitions().get(self.status, set())

    def is_publicly_visible(self) -> bool:
        return self.publish_status == PublishStatus.PUBLISHED and self.status == CaseStatus.APPROVED

    def __repr__(self) -> str:
        return f"<Case {self.case_number} status={self.status}>"
