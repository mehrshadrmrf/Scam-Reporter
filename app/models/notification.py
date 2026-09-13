from __future__ import annotations

from typing import Optional
from uuid import UUID as UUIDType

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class Notification(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """اعلان برای کاربر (مثلاً وقتی پرونده‌ی دنبال‌شده به‌روزرسانی می‌شود)."""
    __tablename__ = "notifications"

    user_id: Mapped[UUIDType] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    case_id: Mapped[Optional[UUIDType]] = mapped_column(UUID(as_uuid=True), ForeignKey("cases.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_sent: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
