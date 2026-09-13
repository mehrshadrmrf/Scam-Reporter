from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import BigInteger, Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import AccountStatus, UserRole

if TYPE_CHECKING:
    from app.models.audit_log import AuditLog
    from app.models.report import Report


class User(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    کاربر سیستم - می‌تواند صرفاً گزارش‌دهنده باشد یا نقش مدیریتی داشته باشد.
    اطلاعات پروفایل از تلگرام همگام‌سازی می‌شود.
    """
    __tablename__ = "users"

    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True, nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    language: Mapped[str] = mapped_column(String(8), default="fa")

    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.REPORTER, nullable=False)
    account_status: Mapped[AccountStatus] = mapped_column(
        Enum(AccountStatus), default=AccountStatus.ACTIVE, nullable=False
    )

    trust_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_reports: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    approved_reports: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    rejected_reports: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    reports: Mapped[List["Report"]] = relationship(back_populates="reporter", lazy="selectin")
    audit_logs: Mapped[List["AuditLog"]] = relationship(back_populates="actor", lazy="selectin")

    @property
    def display_name(self) -> str:
        if self.username:
            return f"@{self.username}"
        return f"{self.first_name or ''} {self.last_name or ''}".strip() or str(self.telegram_id)

    @property
    def is_staff(self) -> bool:
        return self.role in {UserRole.REVIEWER, UserRole.MODERATOR, UserRole.ADMIN, UserRole.SUPER_ADMIN}

    def __repr__(self) -> str:
        return f"<User {self.display_name} role={self.role}>"
