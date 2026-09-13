"""سرویس تولید آمار داشبورد مدیریت - دقیقاً مطابق بخش «داشبورد آماری» در PDD."""
from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.case import Case
from app.models.enums import CaseStatus
from app.models.report import Report
from app.models.user import User


@dataclass
class DashboardStatistics:
    total_reports: int
    reports_today: int
    reports_this_week: int
    reports_this_month: int
    approved_reports: int
    rejected_reports: int
    open_cases: int
    closed_cases: int
    active_users: int


class StatisticsService:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_dashboard_statistics(self) -> DashboardStatistics:
        now = datetime.utcnow()
        today_start = datetime(now.year, now.month, now.day)
        week_start = today_start - timedelta(days=today_start.weekday())
        month_start = datetime(now.year, now.month, 1)

        total_reports = await self._count(select(func.count()).select_from(Report))
        reports_today = await self._count(
            select(func.count()).select_from(Report).where(Report.created_at >= today_start)
        )
        reports_this_week = await self._count(
            select(func.count()).select_from(Report).where(Report.created_at >= week_start)
        )
        reports_this_month = await self._count(
            select(func.count()).select_from(Report).where(Report.created_at >= month_start)
        )
        approved_reports = await self._count(
            select(func.count()).select_from(Case).where(Case.status == CaseStatus.APPROVED)
        )
        rejected_reports = await self._count(
            select(func.count()).select_from(Case).where(Case.status == CaseStatus.REJECTED)
        )
        open_cases = await self._count(
            select(func.count())
            .select_from(Case)
            .where(Case.status.in_([CaseStatus.PENDING_REVIEW, CaseStatus.UNDER_REVIEW, CaseStatus.NEEDS_MORE_EVIDENCE]))
        )
        closed_cases = await self._count(
            select(func.count()).select_from(Case).where(Case.status.in_([CaseStatus.APPROVED, CaseStatus.REJECTED, CaseStatus.ARCHIVED]))
        )
        active_users = await self._count(
            select(func.count()).select_from(User).where(User.total_reports > 0)
        )

        return DashboardStatistics(
            total_reports=total_reports,
            reports_today=reports_today,
            reports_this_week=reports_this_week,
            reports_this_month=reports_this_month,
            approved_reports=approved_reports,
            rejected_reports=rejected_reports,
            open_cases=open_cases,
            closed_cases=closed_cases,
            active_users=active_users,
        )

    async def _count(self, stmt) -> int:
        result = await self._session.execute(stmt)
        return int(result.scalar_one())
