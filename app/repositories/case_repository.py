from typing import Optional, Sequence

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.case import Case
from app.models.enums import CaseStatus, PublishStatus
from app.repositories.base import BaseRepository


class CaseRepository(BaseRepository[Case]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Case)

    async def get_by_case_number(self, case_number: str) -> Optional[Case]:
        stmt = select(Case).where(Case.case_number == case_number)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_matching_open_case(
        self,
        username: Optional[str] = None,
        card_number: Optional[str] = None,
        phone_number: Optional[str] = None,
        wallet_address: Optional[str] = None,
        domain: Optional[str] = None,
    ) -> Optional[Case]:
        """پرونده‌ی باز مرتبط با شناسه‌های داده‌شده را برمی‌گرداند (برای merge خودکار)."""
        conditions = []
        if username:
            conditions.append(Case.subject_username == username)
        if card_number:
            conditions.append(Case.subject_card_number_masked == card_number)
        if phone_number:
            conditions.append(Case.subject_phone_number == phone_number)
        if wallet_address:
            conditions.append(Case.subject_wallet_address == wallet_address)
        if domain:
            conditions.append(Case.subject_domain == domain)

        if not conditions:
            return None

        stmt = select(Case).where(or_(*conditions), Case.status != CaseStatus.ARCHIVED).limit(1)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def search_public(self, query: str, limit: int = 20) -> Sequence[Case]:
        """جستجوی عمومی - فقط در پرونده‌های منتشرشده."""
        like = f"%{query}%"
        stmt = (
            select(Case)
            .where(
                Case.publish_status == PublishStatus.PUBLISHED,
                Case.status == CaseStatus.APPROVED,
                or_(
                    Case.subject_username.ilike(like),
                    Case.subject_phone_number.ilike(like),
                    Case.subject_card_number_masked.ilike(like),
                    Case.subject_wallet_address.ilike(like),
                    Case.subject_domain.ilike(like),
                    Case.subject_profile_link.ilike(like),
                    Case.subject_channel_link.ilike(like),
                    Case.title.ilike(like),
                ),
            )
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def list_by_status(self, status: CaseStatus, limit: int = 50, offset: int = 0) -> Sequence[Case]:
        stmt = select(Case).where(Case.status == status).limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        return result.scalars().all()
