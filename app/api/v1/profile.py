from fastapi import APIRouter

from app.api.deps import CurrentUser
from app.schemas.user import UserProfileSchema

router = APIRouter(prefix="/profile", tags=["Profile"])


@router.get("", response_model=UserProfileSchema)
async def get_my_profile(current_user: CurrentUser):
    return current_user
