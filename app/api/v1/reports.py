"""Endpoint های مربوط به ثبت گزارش."""
from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.deps import CurrentUser, get_report_service
from app.schemas.report import ReportCreateSchema, ReportReadSchema
from app.services.report_service import ReportService, SubmitReportCommand

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.post("", response_model=ReportReadSchema, status_code=status.HTTP_201_CREATED)
async def submit_report(
    payload: ReportCreateSchema,
    current_user: CurrentUser,
    report_service: Annotated[ReportService, Depends(get_report_service)],
):
    """ثبت گزارش جدید توسط کاربر لاگین‌شده (از طریق بات یا مستقیماً API)."""
    command = SubmitReportCommand(reporter_id=current_user.id, **payload.model_dump())
    report = await report_service.submit(command)
    return report
