from fastapi import APIRouter, Request
from core.auth import get_current_user_id
from db.database import get_pool

router = APIRouter(prefix="/api/categories", tags=["categories"])


@router.get("")
async def list_categories(request: Request):
    user_id = get_current_user_id(request)

    pool = get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT id, name, type
            FROM categories
            WHERE user_id = $1
            ORDER BY name
        """, user_id)

    return [dict(r) for r in rows]
