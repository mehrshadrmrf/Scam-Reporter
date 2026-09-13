"""نقطه ورود اجرای بات تلگرام (Aiogram 3، Long Polling)."""
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage

from app.bot.handlers import profile, report_flow, search, start
from app.core.config import settings
from app.core.logging import configure_logging, get_logger

configure_logging()
logger = get_logger(__name__)


def create_dispatcher() -> Dispatcher:
    """
    از RedisStorage برای FSM استفاده می‌شود تا وضعیت مکالمه بین ری‌استارت‌های
    بات یا در استقرار چندنسخه‌ای (horizontal scaling) از دست نرود.
    """
    storage = RedisStorage.from_url(settings.redis_url)
    dispatcher = Dispatcher(storage=storage)

    dispatcher.include_router(start.router)
    dispatcher.include_router(report_flow.router)
    dispatcher.include_router(search.router)
    dispatcher.include_router(profile.router)

    return dispatcher


async def main() -> None:
    if not settings.bot_token:
        raise RuntimeError("BOT_TOKEN تنظیم نشده است. آن را در فایل .env مقداردهی کنید.")

    bot = Bot(token=settings.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dispatcher = create_dispatcher()

    logger.info("bot_starting")
    await bot.delete_webhook(drop_pending_updates=True)
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
