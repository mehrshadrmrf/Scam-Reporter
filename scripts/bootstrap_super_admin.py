"""اجرای یک‌باره: ارتقای یک کاربر موجود (بر اساس Telegram ID) به نقش Super Admin.

اجرا:
    python -m scripts.bootstrap_super_admin <telegram_id>
"""
import asyncio
import sys

from app.core.database import db_session_context
from app.models.enums import UserRole
from app.repositories.user_repository import UserRepository


async def bootstrap_super_admin(telegram_id: int) -> None:
    async with db_session_context() as session:
        users = UserRepository(session)
        user = await users.get_or_create(telegram_id=telegram_id, username=None, first_name=None, last_name=None)
        user.role = UserRole.SUPER_ADMIN
        await session.commit()
    print(f"✅ کاربر با Telegram ID {telegram_id} اکنون Super Admin است.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("استفاده صحیح: python -m scripts.bootstrap_super_admin <telegram_id>")
        sys.exit(1)
    asyncio.run(bootstrap_super_admin(int(sys.argv[1])))
