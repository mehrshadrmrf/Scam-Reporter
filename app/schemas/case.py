from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.models.enums import CaseStatus, Priority, PublishStatus, ReportCategory


class CasePublicSchema(BaseModel):
    """خروجی عمومی - فقط فیلدهای امن و Mask‌شده (بدون داده خام حساس)."""
    case_number: str
    title: str
    category: ReportCategory
    status: CaseStatus
    total_reports: int
    summary: Optional[str]
    subject_username: Optional[str]
    subject_card_number_masked: Optional[str]
    subject_domain: Optional[str]
    first_incident_date: Optional[date]
    updated_at: datetime

    model_config = {"from_attributes": True}


class CaseAdminSchema(CasePublicSchema):
    """خروجی کامل برای پنل مدیریت."""
    id: UUID
    priority: Priority
    publish_status: PublishStatus
    subject_phone_number: Optional[str]
    subject_wallet_address: Optional[str]
    subject_profile_link: Optional[str]
    total_damage_amount: int
    created_at: datetime


class ReviewActionSchema(BaseModel):
    note: Optional[str] = None


class RejectActionSchema(BaseModel):
    note: str
