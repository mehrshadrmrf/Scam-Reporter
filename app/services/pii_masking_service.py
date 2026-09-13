"""
سرویس مسئول Mask کردن داده‌های حساس (شماره کارت/تلفن) پیش از نمایش عمومی.
این جداسازی طبق توصیه حقوقی/حریم‌خصوصی سند طراحی است:
داده خام فقط برای مدیران و بررسی داخلی نگهداری می‌شود.
"""
import re


class PIIMaskingService:
    @staticmethod
    def mask_card_number(card_number: str | None) -> str | None:
        if not card_number:
            return None
        digits = re.sub(r"\D", "", card_number)
        if len(digits) < 8:
            return "*" * len(digits)
        return f"{digits[:6]}{'*' * (len(digits) - 10)}{digits[-4:]}"

    @staticmethod
    def mask_phone_number(phone_number: str | None) -> str | None:
        if not phone_number:
            return None
        digits = re.sub(r"\D", "", phone_number)
        if len(digits) < 6:
            return "*" * len(digits)
        return f"{digits[:4]}{'*' * (len(digits) - 6)}{digits[-2:]}"
