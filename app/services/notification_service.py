"""
سرویس اعلان‌ها. در این نسخه، «دنبال‌کنندگان» یک پرونده معادل گزارش‌دهندگانی
هستند که در آن پرونده گزارش ثبت کرده‌اند (ساده‌ترین و امن‌ترین تعریف اولیه).
تحویل واقعی پیام (ارسال به تلگرام) بر عهده‌ی Worker جداگانه در بات است که
Notification های is_sent=False را از صف Redis/دیتابیس پردازش می‌کند.
"""
from app.models.case import Case
from app.models.notification import Notification
from app.repositories.audit_notification_repository import NotificationRepository
from app.repositories.report_repository import ReportRepository


class NotificationService:
    def __init__(self, notification_repository: NotificationRepository, report_repository: ReportRepository):
        self._notifications = notification_repository
        self._reports = report_repository

    async def notify_case_followers(self, case: Case, title: str, body: str) -> list[Notification]:
        reports = await self._reports.list_by_case(case.id)
        reporter_ids = {r.reporter_id for r in reports}

        created: list[Notification] = []
        for reporter_id in reporter_ids:
            notification = Notification(
                user_id=reporter_id,
                case_id=case.id,
                title=f"{title} - پرونده {case.case_number}",
                body=body,
            )
            self._notifications.add(notification)
            created.append(notification)

        await self._notifications.flush()
        return created
