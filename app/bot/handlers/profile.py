from aiogram import F, Router
from aiogram.types import Message

from app.bot.container import bot_services
from app.bot.keyboards.main_menu import main_menu_keyboard
from app.models.enums import AccountStatus

router = Router(name="profile")

_STATUS_LABELS = {
    AccountStatus.ACTIVE: "✅ فعال",
    AccountStatus.RESTRICTED: "⚠️ محدود",
    AccountStatus.BANNED: "⛔️ مسدود",
}


@router.message(F.text == "👤 پروفایل من")
async def show_profile(message: Message) -> None:
    async with bot_services() as services:
        user = await services.users.get_or_create(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
        )
        await services.session.commit()

        text = (
            "👤 <b>پروفایل شما</b>\n\n"
            f"وضعیت حساب: {_STATUS_LABELS.get(user.account_status, user.account_status.value)}\n"
            f"امتیاز اعتبار: <b>{user.trust_score}</b>\n"
            f"تعداد کل گزارش‌ها: {user.total_reports}\n"
            f"گزارش‌های تأییدشده: {user.approved_reports}\n"
            f"گزارش‌های ردشده: {user.rejected_reports}\n"
        )
    await message.answer(text, reply_markup=main_menu_keyboard())
