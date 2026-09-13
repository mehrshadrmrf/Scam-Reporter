from __future__ import annotations

from typing import TYPE_CHECKING, Optional
from uuid import UUID as UUIDType

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import EvidenceType

if TYPE_CHECKING:
    from app.models.case import Case
    from app.models.report import Report


class Evidence(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """مدرک ضمیمه‌شده به یک گزارش (فایل، عکس، ویدئو یا اسکرین‌شات چت)."""
    __tablename__ = "evidence"

    report_id: Mapped[UUIDType] = mapped_column(UUID(as_uuid=True), ForeignKey("reports.id"), nullable=False)
    case_id: Mapped[Optional[UUIDType]] = mapped_column(UUID(as_uuid=True), ForeignKey("cases.id"), nullable=True)

    evidence_type: Mapped[EvidenceType] = mapped_column(Enum(EvidenceType), nullable=False)
    storage_key: Mapped[str] = mapped_column(String(512), nullable=False)  # مسیر در MinIO/S3
    file_hash: Mapped[str] = mapped_column(String(128), index=True, nullable=False)  # برای تشخیص تکراری
    mime_type: Mapped[str] = mapped_column(String(128), nullable=False)
    ocr_extracted_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    is_publishable: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_corrupted: Mapped[bool] = mapped_column(default=False, nullable=False)

    report: Mapped["Report"] = relationship(back_populates="evidence")
    case: Mapped[Optional["Case"]] = relationship(back_populates="evidence")

    def __repr__(self) -> str:
        return f"<Evidence {self.id} type={self.evidence_type}>"
