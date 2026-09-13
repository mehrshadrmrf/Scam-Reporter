"""
پیاده‌سازی فرآیند گام‌به‌گام ثبت گزارش از طریق مکالمه با بات.
هر مرحله دقیقاً یکی از فیلدهای فرم ثبت گزارش در PDD است.
داده‌ها در FSMContext نگهداری می‌شوند تا در پایان به ReportService ارسال شوند.
"""
from datetime import datetime

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.bot.container import bot_services
from app.bot.keyboards.main_menu import (
    category_keyboard,
    category_label,
    confirm_keyboard,
    main_menu_keyboard,
    skip_keyboard,
)
from app.bot.states.report_states import ReportFlowStates
from app.core.exceptions import ScamReportException
from app.models.enums import ReportCategory
from app.services.report_service import SubmitReportCommand

router = Router(name="report_flow")


@router.message(F.text == "🚨 ثبت گزارش جدید")
async def start_report_flow(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(ReportFlowStates.choosing_category)
    await message.answer("لطفاً دسته‌بندی گزارش را انتخاب کنید:", reply_markup=category_keyboard())


@router.callback_query(ReportFlowStates.choosing_category, F.data.startswith("category:"))
async def choose_category(callback: CallbackQuery, state: FSMContext) -> None:
    category_value = callback.data.split(":", 1)[1]
    await state.update_data(category=category_value)
    await state.set_state(ReportFlowStates.entering_subject_name)
    await callback.message.edit_text(f"دسته‌بندی انتخاب‌شده: {category_label(ReportCategory(category_value))}")
    await callback.message.answer(
        "نام یا شناسه فرد/کسب‌وکار مورد گزارش را وارد کنید (یا /skip برای رد شدن):"
    )
    await callback.answer()


async def _handle_skippable_step(
    message: Message, state: FSMContext, field_name: str, next_state, prompt: str, keyboard=None
) -> None:
    value = None if message.text and message.text.strip() == "/skip" else message.text
    await state.update_data(**{field_name: value})
    await state.set_state(next_state)
    await message.answer(prompt, reply_markup=keyboard or skip_keyboard())


@router.message(ReportFlowStates.entering_subject_name)
async def enter_subject_name(message: Message, state: FSMContext) -> None:
    await _handle_skippable_step(
        message, state, "subject_name", ReportFlowStates.entering_subject_username,
        "نام کاربری (Username) طرف مقابل را وارد کنید (یا /skip):",
    )


@router.message(ReportFlowStates.entering_subject_username)
async def enter_subject_username(message: Message, state: FSMContext) -> None:
    await _handle_skippable_step(
        message, state, "subject_username", ReportFlowStates.entering_profile_link,
        "لینک پروفایل را وارد کنید (یا /skip):",
    )


@router.message(ReportFlowStates.entering_profile_link)
async def enter_profile_link(message: Message, state: FSMContext) -> None:
    await _handle_skippable_step(
        message, state, "subject_profile_link", ReportFlowStates.entering_channel_link,
        "لینک کانال (در صورت وجود) را وارد کنید (یا /skip):",
    )


@router.message(ReportFlowStates.entering_channel_link)
async def enter_channel_link(message: Message, state: FSMContext) -> None:
    await _handle_skippable_step(
        message, state, "subject_channel_link", ReportFlowStates.entering_group_link,
        "لینک گروه (در صورت وجود) را وارد کنید (یا /skip):",
    )


@router.message(ReportFlowStates.entering_group_link)
async def enter_group_link(message: Message, state: FSMContext) -> None:
    await _handle_skippable_step(
        message, state, "subject_group_link", ReportFlowStates.entering_card_number,
        "شماره کارت طرف مقابل را وارد کنید (یا /skip):",
    )


@router.message(ReportFlowStates.entering_card_number)
async def enter_card_number(message: Message, state: FSMContext) -> None:
    await _handle_skippable_step(
        message, state, "subject_card_number", ReportFlowStates.entering_phone_number,
        "شماره تلفن طرف مقابل را وارد کنید (یا /skip):",
    )


@router.message(ReportFlowStates.entering_phone_number)
async def enter_phone_number(message: Message, state: FSMContext) -> None:
    await _handle_skippable_step(
        message, state, "subject_phone_number", ReportFlowStates.entering_wallet_address,
        "آدرس کیف‌پول رمزارز طرف مقابل را وارد کنید (یا /skip):",
    )


@router.message(ReportFlowStates.entering_wallet_address)
async def enter_wallet_address(message: Message, state: FSMContext) -> None:
    await _handle_skippable_step(
        message, state, "subject_wallet_address", ReportFlowStates.entering_domain,
        "دامنه یا وب‌سایت طرف مقابل را وارد کنید (یا /skip):",
    )


@router.message(ReportFlowStates.entering_domain)
async def enter_domain(message: Message, state: FSMContext) -> None:
    value = None if message.text.strip() == "/skip" else message.text
    await state.update_data(subject_domain=value)
    await state.set_state(ReportFlowStates.entering_description)
    await message.answer(
        "✍️ حالا توضیح کامل ماجرا را بنویسید (حداقل ۲۰ کاراکتر، این فیلد اجباری است):"
    )


@router.message(ReportFlowStates.entering_description)
async def enter_description(message: Message, state: FSMContext) -> None:
    if not message.text or len(message.text.strip()) < 20:
        await message.answer("⚠️ توضیحات باید حداقل ۲۰ کاراکتر باشد. لطفاً دوباره بنویسید:")
        return
    await state.update_data(description=message.text)
    await state.set_state(ReportFlowStates.entering_damage_amount)
    await message.answer("مبلغ خسارت را به تومان وارد کنید (فقط عدد، یا /skip):")


@router.message(ReportFlowStates.entering_damage_amount)
async def enter_damage_amount(message: Message, state: FSMContext) -> None:
    text = message.text.strip()
    if text == "/skip":
        amount = None
    elif text.isdigit():
        amount = int(text)
    else:
        await message.answer("⚠️ لطفاً فقط عدد وارد کنید یا /skip بزنید.")
        return
    await state.update_data(damage_amount=amount)
    await state.set_state(ReportFlowStates.entering_incident_date)
    await message.answer("تاریخ وقوع را به شکل YYYY-MM-DD وارد کنید (یا /skip):")


@router.message(ReportFlowStates.entering_incident_date)
async def enter_incident_date(message: Message, state: FSMContext) -> None:
    text = message.text.strip()
    incident_date = None
    if text != "/skip":
        try:
            incident_date = datetime.strptime(text, "%Y-%m-%d").date()
        except ValueError:
            await message.answer("⚠️ فرمت تاریخ نامعتبر است. مثال صحیح: 2026-05-01 (یا /skip بزنید).")
            return

    await state.update_data(incident_date=incident_date.isoformat() if incident_date else None)
    data = await state.get_data()
    summary = _build_summary(data)
    await state.set_state(ReportFlowStates.confirming)
    await message.answer(summary, reply_markup=confirm_keyboard())


def _build_summary(data: dict) -> str:
    lines = ["📋 <b>پیش‌نمایش گزارش شما:</b>\n"]
    label_map = {
        "subject_name": "نام/شناسه",
        "subject_username": "Username",
        "subject_profile_link": "لینک پروفایل",
        "subject_channel_link": "لینک کانال",
        "subject_group_link": "لینک گروه",
        "subject_card_number": "شماره کارت",
        "subject_phone_number": "شماره تلفن",
        "subject_wallet_address": "کیف پول",
        "subject_domain": "دامنه",
        "damage_amount": "مبلغ خسارت",
        "incident_date": "تاریخ وقوع",
    }
    for field, label in label_map.items():
        value = data.get(field)
        if value:
            lines.append(f"• {label}: {value}")
    lines.append(f"\n📝 توضیحات:\n{data.get('description', '')}")
    lines.append("\nآیا گزارش ثبت شود؟")
    return "\n".join(lines)


@router.callback_query(ReportFlowStates.confirming, F.data == "confirm_submit")
async def confirm_submit(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    incident_date = None
    if data.get("incident_date"):
        incident_date = datetime.fromisoformat(data["incident_date"]).date()

    async with bot_services() as services:
        user = await services.users.get_or_create(
            telegram_id=callback.from_user.id,
            username=callback.from_user.username,
            first_name=callback.from_user.first_name,
            last_name=callback.from_user.last_name,
        )
        await services.session.flush()

        command = SubmitReportCommand(
            reporter_id=user.id,
            category=ReportCategory(data["category"]),
            description=data["description"],
            subject_name=data.get("subject_name"),
            subject_username=data.get("subject_username"),
            subject_profile_link=data.get("subject_profile_link"),
            subject_channel_link=data.get("subject_channel_link"),
            subject_group_link=data.get("subject_group_link"),
            subject_card_number=data.get("subject_card_number"),
            subject_phone_number=data.get("subject_phone_number"),
            subject_wallet_address=data.get("subject_wallet_address"),
            subject_domain=data.get("subject_domain"),
            damage_amount=data.get("damage_amount"),
            incident_date=incident_date,
        )
        try:
            report = await services.report_service.submit(command)
            case = report.case
            await callback.message.edit_text(
                f"✅ گزارش شما با موفقیت ثبت شد.\n\n"
                f"شماره پرونده: <code>{case.case_number if case else '-'}</code>\n"
                "پس از بررسی توسط تیم ما، نتیجه به شما اطلاع داده خواهد شد."
            )
        except ScamReportException as exc:
            await callback.message.edit_text(f"❌ خطا در ثبت گزارش: {exc.message}")

    await state.clear()
    await callback.message.answer("منوی اصلی:", reply_markup=main_menu_keyboard())
    await callback.answer()


@router.callback_query(ReportFlowStates.confirming, F.data == "cancel_submit")
async def cancel_submit(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_text("عملیات ثبت گزارش لغو شد.")
    await callback.message.answer("منوی اصلی:", reply_markup=main_menu_keyboard())
    await callback.answer()
