from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import ReportCategory


class ReportCreateSchema(BaseModel):
    category: ReportCategory
    description: str = Field(min_length=20, max_length=5000)
    subject_name: Optional[str] = Field(default=None, max_length=256)
    subject_username: Optional[str] = Field(default=None, max_length=128)
    subject_profile_link: Optional[str] = Field(default=None, max_length=512)
    subject_channel_link: Optional[str] = Field(default=None, max_length=512)
    subject_group_link: Optional[str] = Field(default=None, max_length=512)
    subject_card_number: Optional[str] = Field(default=None, max_length=32)
    subject_phone_number: Optional[str] = Field(default=None, max_length=32)
    subject_wallet_address: Optional[str] = Field(default=None, max_length=128)
    subject_domain: Optional[str] = Field(default=None, max_length=256)
    damage_amount: Optional[int] = Field(default=None, ge=0)
    incident_date: Optional[date] = None


class ReportReadSchema(BaseModel):
    id: UUID
    case_id: Optional[UUID]
    category: ReportCategory
    description: str
    is_duplicate: bool
    created_at: datetime

    model_config = {"from_attributes": True}
