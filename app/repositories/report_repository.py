from typing import Sequence
from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.report import Report
from app.repositories.base import BaseRepository


class ReportRepository(BaseRepository[Report]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Report)

    async def find_potential_duplicates(self, report: Report) -> Sequence[Report]:
        """
        گزارش‌های مشابه را بر اساس شناسه‌های یکتای طرف گزارش‌شده پیدا می‌کند
        (username، شماره کارت، شماره تلفن، آدرس کیف پول، دامنه).
        این نتیجه سپس در DuplicateDetectionService با fuzzy-matching متن ترکیب می‌شود.
        """
        conditions = []
        if report.subject_username:
            conditions.append(Report.subject_username == report.subject_username)
        if report.subject_card_number:
            conditions.append(Report.subject_card_number == report.subject_card_number)
        if report.subject_phone_number:
            conditions.append(Report.subject_phone_number == report.subject_phone_number)
        if report.subject_wallet_address:
            conditions.append(Report.subject_wallet_address == report.subject_wallet_address)
        if report.subject_domain:
            conditions.append(Report.subject_domain == report.subject_domain)

        if not conditions:
            return []

        stmt = select(Report).where(or_(*conditions), Report.id != report.id)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def list_by_case(self, case_id: UUID) -> Sequence[Report]:
        stmt = select(Report).where(Report.case_id == case_id)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def list_by_reporter(self, reporter_id: UUID) -> Sequence[Report]:
        stmt = select(Report).where(Report.reporter_id == reporter_id)
        result = await self._session.execute(stmt)
        return result.scalars().all()
