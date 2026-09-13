"""اجرای یک‌باره: پر کردن جدول Category با دسته‌بندی‌های پیش‌فرض PDD.

اجرا:
    python -m scripts.seed_categories
"""
import asyncio

from sqlalchemy import select

from app.core.database import db_session_context
from app.models.category import Category
from app.models.enums import ReportCategory

_DEFAULT_CATEGORIES: dict[ReportCategory, tuple[str, str]] = {
    ReportCategory.FINANCIAL_FRAUD: ("کلاهبرداری مالی", "برداشت غیرمجاز یا فریب مالی مستقیم"),
    ReportCategory.FAKE_PRODUCT: ("فروش کالای جعلی", "ارسال نکردن کالا یا ارسال کالای غیراصل"),
    ReportCategory.FAKE_COURSE_OR_SERVICE: ("فروش دوره یا خدمات جعلی", "خدمات یا آموزش‌های ارائه‌نشده یا کم‌کیفیت"),
    ReportCategory.IMPERSONATION: ("جعل هویت", "جعل هویت فرد یا برند دیگر"),
    ReportCategory.PHISHING: ("فیشینگ", "سرقت اطلاعات از طریق لینک یا صفحه جعلی"),
    ReportCategory.EXTORTION: ("اخاذی", "تهدید به انتشار اطلاعات برای دریافت پول"),
    ReportCategory.HACKING: ("هک", "نفوذ غیرمجاز به حساب یا سیستم"),
    ReportCategory.MISLEADING_ADS: ("تبلیغات گمراه‌کننده", "ادعاهای نادرست در تبلیغات"),
    ReportCategory.PONZI_SCHEME: ("سرمایه‌گذاری یا پانزی", "طرح‌های هرمی و سرمایه‌گذاری کاذب"),
    ReportCategory.CRYPTOCURRENCY: ("ارز دیجیتال", "کلاهبرداری مرتبط با رمزارزها"),
    ReportCategory.GAMBLING: ("شرط‌بندی", "سایت‌ها و اپلیکیشن‌های شرط‌بندی متقلبانه"),
    ReportCategory.OTHER: ("سایر", "سایر موارد که در دسته‌های بالا جای نمی‌گیرند"),
}


async def seed_categories() -> None:
    async with db_session_context() as session:
        existing = (await session.execute(select(Category.key))).scalars().all()
        existing_keys = set(existing)

        for key, (title_fa, description) in _DEFAULT_CATEGORIES.items():
            if key in existing_keys:
                continue
            session.add(Category(key=key, title_fa=title_fa, description=description))

        await session.commit()
    print("✅ دسته‌بندی‌های پیش‌فرض با موفقیت ثبت شدند.")


if __name__ == "__main__":
    asyncio.run(seed_categories())
