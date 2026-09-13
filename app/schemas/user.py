from uuid import UUID

from pydantic import BaseModel

from app.models.enums import AccountStatus, UserRole


class UserProfileSchema(BaseModel):
    id: UUID
    telegram_id: int
    username: str | None
    role: UserRole
    account_status: AccountStatus
    trust_score: int
    total_reports: int
    approved_reports: int
    rejected_reports: int

    model_config = {"from_attributes": True}
