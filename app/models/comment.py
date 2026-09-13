from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID as UUIDType

from sqlalchemy import Boolean, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.case import Case
    from app.models.user import User


class Comment(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """یادداشت داخلی تیم بررسی روی یک پرونده (هرگز عمومی منتشر نمی‌شود)."""
    __tablename__ = "comments"

    case_id: Mapped[UUIDType] = mapped_column(UUID(as_uuid=True), ForeignKey("cases.id"), nullable=False)
    author_id: Mapped[UUIDType] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    is_internal: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    case: Mapped["Case"] = relationship(back_populates="comments")
    author: Mapped["User"] = relationship(lazy="joined")
