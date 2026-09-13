from __future__ import annotations

from typing import Optional
from uuid import UUID as UUIDType

from sqlalchemy import Enum, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import TrustScoreReason


class ReporterScoreHistory(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """تاریخچه هر تغییر در Trust Score یک کاربر - شفاف و قابل ممیزی."""
    __tablename__ = "reporter_score_history"

    user_id: Mapped[UUIDType] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    reason: Mapped[TrustScoreReason] = mapped_column(Enum(TrustScoreReason), nullable=False)
    delta: Mapped[int] = mapped_column(Integer, nullable=False)
    resulting_score: Mapped[int] = mapped_column(Integer, nullable=False)
    related_report_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
