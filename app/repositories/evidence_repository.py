from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.evidence import Evidence
from app.repositories.base import BaseRepository


class EvidenceRepository(BaseRepository[Evidence]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Evidence)

    async def get_by_file_hash(self, file_hash: str) -> Optional[Evidence]:
        """برای تشخیص فایل تکراری بر اساس هش محتوا."""
        stmt = select(Evidence).where(Evidence.file_hash == file_hash)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
