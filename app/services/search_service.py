from typing import Sequence

from app.core.exceptions import ValidationError
from app.models.case import Case
from app.repositories.case_repository import CaseRepository


class SearchService:
    def __init__(self, case_repository: CaseRepository):
        self._cases = case_repository

    async def search(self, query: str, limit: int = 20) -> Sequence[Case]:
        query = query.strip()
        if len(query) < 3:
            raise ValidationError("عبارت جستجو باید حداقل ۳ کاراکتر باشد.")
        return await self._cases.search_public(query, limit=limit)
