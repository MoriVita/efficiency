from fastapi import APIRouter, Request
from core.auth import get_current_user_id
from db.database import get_pool

router = APIRouter(prefix="/api/goals", tags=["goals"])


@router.get("")
async def list_goals(request: Request):
    user_id = await get_current_user_id(request)
    pool = get_pool()

    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT id, name, target_amount
            FROM goals
            WHERE user_id = $1
            ORDER BY created_at
        """, user_id)

    return [dict(r) for r in rows]


@router.post("")
async def create_goal(request: Request, data: dict):
    user_id = await get_current_user_id(request)
    pool = get_pool()

    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO goals (user_id, name, target_amount)
            VALUES ($1, $2, $3)
        """, user_id, data["name"], data["target_amount"])

    return {"status":"ok"}
