from __future__ import annotations

from typing import TYPE_CHECKING, Optional
from uuid import UUID as UUIDType

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import AuditAction

if TYPE_CHECKING:
    from app.models.user import User


class AuditLog(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """ثبت غیرقابل‌تغییر (append-only) تمام عملیات حساس برای پاسخگویی و شفافیت."""
    __tablename__ = "audit_logs"

    actor_id: Mapped[UUIDType] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    action: Mapped[AuditAction] = mapped_column(Enum(AuditAction), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(64), nullable=False)
    entity_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    actor: Mapped["User"] = relationship(back_populates="audit_logs", lazy="joined")

    def __repr__(self) -> str:
        return f"<AuditLog {self.action} by={self.actor_id}>"
