"""Endpoint های «عملیات مدیر» روی پرونده (تأیید، رد، درخواست مدارک، انتشار)."""
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.deps import StaffUser, get_case_service
from app.schemas.case import CaseAdminSchema, RejectActionSchema, ReviewActionSchema
from app.services.case_service import CaseService

router = APIRouter(prefix="/review", tags=["Review"])


@router.post("/{case_id}/start", response_model=CaseAdminSchema)
async def start_review(
    case_id: UUID,
    staff_user: StaffUser,
    case_service: Annotated[CaseService, Depends(get_case_service)],
):
    return await case_service.start_review(case_id, staff_user)


@router.post("/{case_id}/request-evidence", response_model=CaseAdminSchema)
async def request_more_evidence(
    case_id: UUID,
    payload: RejectActionSchema,
    staff_user: StaffUser,
    case_service: Annotated[CaseService, Depends(get_case_service)],
):
    return await case_service.request_more_evidence(case_id, staff_user, payload.note)


@router.post("/{case_id}/approve", response_model=CaseAdminSchema)
async def approve_case(
    case_id: UUID,
    payload: ReviewActionSchema,
    staff_user: StaffUser,
    case_service: Annotated[CaseService, Depends(get_case_service)],
):
    return await case_service.approve(case_id, staff_user, payload.note)


@router.post("/{case_id}/reject", response_model=CaseAdminSchema)
async def reject_case(
    case_id: UUID,
    payload: RejectActionSchema,
    staff_user: StaffUser,
    case_service: Annotated[CaseService, Depends(get_case_service)],
):
    return await case_service.reject(case_id, staff_user, payload.note)


@router.post("/{case_id}/publish", response_model=CaseAdminSchema)
async def publish_case(
    case_id: UUID,
    staff_user: StaffUser,
    case_service: Annotated[CaseService, Depends(get_case_service)],
):
    return await case_service.publish(case_id, staff_user)


@router.post("/{case_id}/hide", response_model=CaseAdminSchema)
async def hide_case(
    case_id: UUID,
    payload: RejectActionSchema,
    staff_user: StaffUser,
    case_service: Annotated[CaseService, Depends(get_case_service)],
):
    return await case_service.hide(case_id, staff_user, payload.note)
