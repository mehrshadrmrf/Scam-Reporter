from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

from app.models.enums import ReportCategory

_CATEGORY_LABELS: dict[ReportCategory, str] = {
    ReportCategory.FINANCIAL_FRAUD: "💰 کلاهبرداری مالی",
    ReportCategory.FAKE_PRODUCT: "📦 فروش کالای جعلی",
    ReportCategory.FAKE_COURSE_OR_SERVICE: "🎓 دوره/خدمات جعلی",
    ReportCategory.IMPERSONATION: "🎭 جعل هویت",
    ReportCategory.PHISHING: "🎣 فیشینگ",
    ReportCategory.EXTORTION: "⚠️ اخاذی",
    ReportCategory.HACKING: "💻 هک",
    ReportCategory.MISLEADING_ADS: "📢 تبلیغات گمراه‌کننده",
    ReportCategory.PONZI_SCHEME: "📉 سرمایه‌گذاری/پانزی",
    ReportCategory.CRYPTOCURRENCY: "🪙 ارز دیجیتال",
    ReportCategory.GAMBLING: "🎰 شرط‌بندی",
    ReportCategory.OTHER: "❓ سایر",
}


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🚨 ثبت گزارش جدید")],
            [KeyboardButton(text="🔍 جستجو"), KeyboardButton(text="👤 پروفایل من")],
            [KeyboardButton(text="ℹ️ راهنما")],
        ],
        resize_keyboard=True,
    )


def category_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=label, callback_data=f"category:{key.value}")]
        for key, label in _CATEGORY_LABELS.items()
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def skip_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="⏭ رد شدن (اختیاری)", callback_data="skip")]]
    )


def confirm_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ ثبت نهایی گزارش", callback_data="confirm_submit"),
                InlineKeyboardButton(text="❌ انصراف", callback_data="cancel_submit"),
            ]
        ]
    )


def category_label(category: ReportCategory) -> str:
    return _CATEGORY_LABELS.get(category, category.value)
