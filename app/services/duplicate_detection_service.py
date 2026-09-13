"""
سرویس تشخیص تکراری بودن گزارش‌ها.
ترکیبی از تطابق دقیق فیلدهای شناسه (username/کارت/تلفن/کیف‌پول/دامنه)
و شباهت فازی متن توضیحات (rapidfuzz) - دقیقاً مطابق بخش «موتور بررسی اولیه» در PDD.
"""
from dataclasses import dataclass
from typing import Optional, Sequence

from rapidfuzz import fuzz

from app.models.report import Report
from app.repositories.report_repository import ReportRepository

TEXT_SIMILARITY_THRESHOLD = 80  # درصد شباهت متن برای در نظر گرفتن به‌عنوان تکراری


@dataclass
class DuplicateCheckResult:
    is_duplicate: bool
    matched_report: Optional[Report] = None
    similarity_score: float = 0.0
    matched_by: str = ""  # "identity_field" | "text_similarity"


class DuplicateDetectionService:
    def __init__(self, report_repository: ReportRepository):
        self._reports = report_repository

    async def check(self, new_report: Report) -> DuplicateCheckResult:
        candidates: Sequence[Report] = await self._reports.find_potential_duplicates(new_report)

        # ۱. تطابق دقیق روی شناسه‌های یکتا (سریع‌ترین و مطمئن‌ترین راه)
        if candidates:
            best = candidates[0]
            return DuplicateCheckResult(
                is_duplicate=True, matched_report=best, similarity_score=100.0, matched_by="identity_field"
            )

        # ۲. شباهت فازی متن توضیحات در میان گزارش‌های اخیر همان دسته
        # (در نسخه‌ی تولیدی، این بخش با pgvector/embedding در مقیاس بزرگ جایگزین می‌شود)
        recent_reports = await self._reports.list_all(limit=200)
        for candidate in recent_reports:
            if candidate.id == new_report.id or candidate.category != new_report.category:
                continue
            score = fuzz.token_set_ratio(new_report.description, candidate.description)
            if score >= TEXT_SIMILARITY_THRESHOLD:
                return DuplicateCheckResult(
                    is_duplicate=True,
                    matched_report=candidate,
                    similarity_score=float(score),
                    matched_by="text_similarity",
                )

        return DuplicateCheckResult(is_duplicate=False)
