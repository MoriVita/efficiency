from fastapi import Request
from db.database import get_pool


async def get_or_create_user_id(telegram_user_id: int) -> int:
    pool = get_pool()

    async with pool.acquire() as conn:
        user_id = await conn.fetchval(
            "SELECT id FROM app_users WHERE telegram_user_id = $1",
            telegram_user_id
        )

        if user_id:
            return user_id

        return await conn.fetchval(
            """
            INSERT INTO app_users (telegram_user_id)
            VALUES ($1)
            RETURNING id
            """,
            telegram_user_id
        )


async def get_current_user_id(request: Request) -> int:
    """
    Временно: эмуляция Telegram пользователя
    Потом: Telegram.WebApp.initData
    """
    telegram_user_id = 1  # временно для локальной разработки
    return await get_or_create_user_id(telegram_user_id)
