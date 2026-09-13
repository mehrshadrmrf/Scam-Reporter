from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from app.bot.container import bot_services
from app.bot.keyboards.main_menu import main_menu_keyboard

router = Router(name="start")

WELCOME_TEXT = (
    "👋 به <b>ScamReport</b> خوش آمدید.\n\n"
    "این ربات به شما امکان می‌دهد کلاهبرداری‌های فضای مجازی را گزارش کنید، "
    "قبل از انجام معامله سوابق یک شناسه را بررسی کنید و از وضعیت پرونده‌های "
    "خود مطلع شوید.\n\n"
    "⚠️ توجه: هر گزارش پیش از انتشار عمومی توسط تیم بررسی می‌شود. "
    "ثبت گزارش نادرست یا سوءاستفاده از سامانه باعث کاهش امتیاز اعتبار و "
    "در نهایت مسدودی حساب شما خواهد شد."
)

HELP_TEXT = (
    "📖 <b>راهنمای استفاده</b>\n\n"
    "🚨 <b>ثبت گزارش جدید</b> - شروع فرآیند گزارش یک کلاهبرداری\n"
    "🔍 <b>جستجو</b> - بررسی سابقه یک شناسه، لینک، شماره کارت یا کیف‌پول\n"
    "👤 <b>پروفایل من</b> - مشاهده امتیاز اعتبار و وضعیت گزارش‌های شما\n\n"
    "در هر زمان می‌توانید با ارسال /cancel فرآیند جاری را لغو کنید."
)


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    async with bot_services() as services:
        await services.users.get_or_create(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            language=message.from_user.language_code or "fa",
        )
        await services.session.commit()

    await message.answer(WELCOME_TEXT, reply_markup=main_menu_keyboard())


@router.message(Command("help"))
@router.message(F.text == "ℹ️ راهنما")
async def cmd_help(message: Message) -> None:
    await message.answer(HELP_TEXT, reply_markup=main_menu_keyboard())


@router.message(Command("cancel"))
async def cmd_cancel_global(message: Message, state) -> None:
    await state.clear()
    await message.answer("عملیات لغو شد.", reply_markup=main_menu_keyboard())
