"""Endpoint جستجوی عمومی (مطابق «سیستم جستجو» در PDD)."""
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_search_service
from app.schemas.case import CasePublicSchema
from app.services.search_service import SearchService

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("", response_model=list[CasePublicSchema])
async def search_cases(
    q: Annotated[str, Query(min_length=3, description="Username، شماره تلفن، شماره کارت، دامنه یا لینک")],
    search_service: Annotated[SearchService, Depends(get_search_service)],
):
    return await search_service.search(q)
