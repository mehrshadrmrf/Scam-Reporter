from fastapi import APIRouter

from app.api.v1 import cases, profile, review, reports, search, statistics

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(reports.router)
api_router.include_router(cases.router)
api_router.include_router(search.router)
api_router.include_router(review.router)
api_router.include_router(statistics.router)
api_router.include_router(profile.router)
