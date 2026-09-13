from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.bot.container import bot_services
from app.bot.keyboards.main_menu import category_label, main_menu_keyboard
from app.bot.states.report_states import SearchStates
from app.core.exceptions import ValidationError

router = Router(name="search")


@router.message(F.text == "🔍 جستجو")
async def start_search(message: Message, state: FSMContext) -> None:
    await state.set_state(SearchStates.waiting_for_query)
    await message.answer(
        "🔍 Username، شماره تلفن، شماره کارت، آدرس کیف‌پول، دامنه یا لینک مورد نظر را ارسال کنید:"
    )


@router.message(SearchStates.waiting_for_query)
async def run_search(message: Message, state: FSMContext) -> None:
    query = (message.text or "").strip()
    async with bot_services() as services:
        try:
            results = await services.search_service.search(query)
        except ValidationError as exc:
            await message.answer(f"⚠️ {exc.message}")
            return

        if not results:
            await message.answer(
                "✅ هیچ پرونده منتشرشده‌ای برای این عبارت یافت نشد.\n"
                "توجه: نبود نتیجه به‌معنای تأیید اعتبار طرف مقابل نیست؛ همیشه احتیاط کنید."
            )
        else:
            lines = ["⚠️ <b>نتایج مرتبط یافت شد:</b>\n"]
            for case in results:
                lines.append(
                    f"🗂 <code>{case.case_number}</code> - {category_label(case.category)}\n"
                    f"   گزارش‌ها: {case.total_reports} | {case.title}\n"
                )
            lines.append("\nبرای مشاهده جزئیات کامل هر پرونده به وب‌سایت مراجعه کنید.")
            await message.answer("\n".join(lines))

    await state.clear()
    await message.answer("منوی اصلی:", reply_markup=main_menu_keyboard())
