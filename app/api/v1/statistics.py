from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import StaffUser, get_statistics_service
from app.schemas.statistics import DashboardStatisticsSchema
from app.services.statistics_service import StatisticsService

router = APIRouter(prefix="/statistics", tags=["Statistics"])


@router.get("", response_model=DashboardStatisticsSchema)
async def get_statistics(
    staff_user: StaffUser,
    statistics_service: Annotated[StatisticsService, Depends(get_statistics_service)],
):
    stats = await statistics_service.get_dashboard_statistics()
    return stats
