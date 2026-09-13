"""Endpoint های مشاهده و مدیریت پرونده‌ها (مطابق «صفحه پرونده» در PDD)."""
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import StaffUser, get_case_repository
from app.core.exceptions import NotFoundError
from app.repositories.case_repository import CaseRepository
from app.schemas.case import CaseAdminSchema, CasePublicSchema

router = APIRouter(prefix="/cases", tags=["Cases"])


@router.get("/{case_number}", response_model=CasePublicSchema)
async def get_public_case(
    case_number: str,
    case_repo: Annotated[CaseRepository, Depends(get_case_repository)],
):
    """مشاهده عمومی پرونده - فقط پرونده‌های منتشرشده قابل مشاهده هستند."""
    case = await case_repo.get_by_case_number(case_number)
    if case is None or not case.is_publicly_visible():
        raise HTTPException(status.HTTP_404_NOT_FOUND, "پرونده یافت نشد یا هنوز منتشر نشده است.")
    return case


@router.get("/admin/{case_id}", response_model=CaseAdminSchema)
async def get_case_admin(
    case_id: UUID,
    staff_user: StaffUser,
    case_repo: Annotated[CaseRepository, Depends(get_case_repository)],
):
    """مشاهده کامل پرونده برای تیم بررسی (شامل داده‌های حساس)."""
    case = await case_repo.get_by_id(case_id)
    if case is None:
        raise NotFoundError("Case", str(case_id))
    return case
