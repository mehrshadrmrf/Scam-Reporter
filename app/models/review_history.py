from __future__ import annotations

from typing import TYPE_CHECKING, Optional
from uuid import UUID as UUIDType

from sqlalchemy import Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import CaseStatus

if TYPE_CHECKING:
    from app.models.case import Case
    from app.models.user import User


class ReviewHistory(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """تاریخچه هر تغییر وضعیت پرونده - برای نمایش «مشاهده تاریخچه تغییرات» در پنل مدیریت."""
    __tablename__ = "review_history"

    case_id: Mapped[UUIDType] = mapped_column(UUID(as_uuid=True), ForeignKey("cases.id"), nullable=False)
    reviewer_id: Mapped[UUIDType] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    from_status: Mapped[Optional[CaseStatus]] = mapped_column(Enum(CaseStatus), nullable=True)
    to_status: Mapped[CaseStatus] = mapped_column(Enum(CaseStatus), nullable=False)
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    case: Mapped["Case"] = relationship(back_populates="review_history")
    reviewer: Mapped["User"] = relationship(lazy="joined")
