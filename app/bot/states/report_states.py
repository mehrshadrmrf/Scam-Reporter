from aiogram.fsm.state import State, StatesGroup


class ReportFlowStates(StatesGroup):
    """
    مراحل گفت‌وگویی ثبت گزارش - هر مرحله دقیقاً یکی از فیلدهای فرم PDD را می‌پرسد.
    کاربر در هر مرحله می‌تواند با دستور /skip از فیلدهای اختیاری عبور کند.
    """
    choosing_category = State()
    entering_subject_name = State()
    entering_subject_username = State()
    entering_profile_link = State()
    entering_channel_link = State()
    entering_group_link = State()
    entering_card_number = State()
    entering_phone_number = State()
    entering_wallet_address = State()
    entering_domain = State()
    entering_description = State()
    entering_damage_amount = State()
    entering_incident_date = State()
    uploading_evidence = State()
    confirming = State()


class SearchStates(StatesGroup):
    waiting_for_query = State()
