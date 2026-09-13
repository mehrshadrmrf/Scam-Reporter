from pydantic import BaseModel


class DashboardStatisticsSchema(BaseModel):
    total_reports: int
    reports_today: int
    reports_this_week: int
    reports_this_month: int
    approved_reports: int
    rejected_reports: int
    open_cases: int
    closed_cases: int
    active_users: int
