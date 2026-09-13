"""
تنظیمات مرکزی برنامه.
تمام مقادیر پیکربندی از طریق Environment Variables (فایل .env) خوانده می‌شوند
تا هیچ مقدار حساسی داخل کد hardcode نشود.
"""
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App
    app_name: str = "ScamReport"
    app_env: str = "development"
    app_debug: bool = True
    secret_key: str

    # Database
    database_url: str

    # Redis
    redis_url: str = "redis://redis:6379/0"

    # Object storage
    s3_endpoint: str = "minio:9000"
    s3_access_key: str = "minioadmin"
    s3_secret_key: str = "minioadmin"
    s3_bucket: str = "scamreport-evidence"
    s3_secure: bool = False

    # Bot
    bot_token: str = ""
    admin_telegram_ids: str = ""

    # Security
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440

    # Trust score rules
    trust_score_valid_report: int = 10
    trust_score_incomplete_report: int = -5
    trust_score_false_report: int = -20
    trust_score_abuse_attempt: int = -100
    trust_score_ban_threshold: int = -100
    trust_score_restrict_threshold: int = -50

    # Publishing rules
    min_independent_reporters_to_publish: int = 2

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def admin_ids_list(self) -> List[int]:
        return [int(x) for x in self.admin_telegram_ids.split(",") if x.strip().isdigit()]


@lru_cache
def get_settings() -> Settings:
    """Settings را یک‌بار می‌سازد و کش می‌کند (singleton)."""
    return Settings()


settings = get_settings()
