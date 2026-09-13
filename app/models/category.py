from __future__ import annotations

from sqlalchemy import Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import ReportCategory


class Category(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """دسته‌بندی گزارش‌ها - جدا از Enum نگه داشته شده تا بتوان بعداً از UI مدیریت کرد."""
    __tablename__ = "categories"

    key: Mapped[ReportCategory] = mapped_column(Enum(ReportCategory), unique=True, nullable=False)
    title_fa: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str] = mapped_column(String(512), default="")

    def __repr__(self) -> str:
        return f"<Category {self.key}>"
