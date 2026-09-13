from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID as UUIDType

from sqlalchemy import Date, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import ReportCategory

if TYPE_CHECKING:
    from app.models.case import Case
    from app.models.evidence import Evidence
    from app.models.user import User


class Report(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    گزارش خام - دقیقاً همان چیزی که کاربر از طریق بات ارسال می‌کند.
    هر Report در نهایت به یک Case متصل می‌شود (جدید یا merge‌شده با پرونده موجود).
    """
    __tablename__ = "reports"

    reporter_id: Mapped[UUIDType] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    case_id: Mapped[Optional[UUIDType]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cases.id"), nullable=True, index=True
    )

    category: Mapped[ReportCategory] = mapped_column(Enum(ReportCategory), nullable=False)

    # --- اطلاعات طرف گزارش‌شده، دقیقاً مطابق فرم PDD ---
    subject_name: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    subject_username: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    subject_profile_link: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    subject_channel_link: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    subject_group_link: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    subject_card_number: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)  # رمزنگاری‌شده ذخیره می‌شود
    subject_phone_number: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    subject_wallet_address: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    subject_domain: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)

    description: Mapped[str] = mapped_column(Text, nullable=False)
    damage_amount: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    incident_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    is_duplicate: Mapped[bool] = mapped_column(default=False, nullable=False)
    duplicate_of_report_id: Mapped[Optional[UUIDType]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("reports.id"), nullable=True
    )

    reporter: Mapped["User"] = relationship(back_populates="reports", lazy="joined")
    case: Mapped[Optional["Case"]] = relationship(back_populates="reports")
    evidence: Mapped[List["Evidence"]] = relationship(back_populates="report", lazy="selectin")

    def identity_fingerprint_fields(self) -> dict:
        """فیلدهایی که برای تشخیص تکراری بودن استفاده می‌شوند."""
        return {
            "subject_username": self.subject_username,
            "subject_card_number": self.subject_card_number,
            "subject_phone_number": self.subject_phone_number,
            "subject_wallet_address": self.subject_wallet_address,
            "subject_domain": self.subject_domain,
        }

    def __repr__(self) -> str:
        return f"<Report {self.id} category={self.category}>"
