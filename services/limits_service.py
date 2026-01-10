from db.database import get_pool
from models.schemas import LimitIn


async def get_limits(filters: dict):
    query = "SELECT * FROM limits WHERE 1=1"
    values = []
    idx = 1

    for key, value in filters.items():
        query += f" AND {key} = ${idx}"
        values.append(value)
        idx += 1
    pool = get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(query, *values)
        return [dict(row) for row in rows]


async def save_limit(limit: LimitIn):
    pool = get_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            existing = await conn.fetchrow("""
                SELECT id FROM limits
                WHERE user_id=$1 AND category=$2 AND month=$3 AND year=$4
            """, limit.user_id, limit.category, limit.month, limit.year)

            if existing:
                await conn.execute("""
                    UPDATE limits
                    SET monthly_limit=$1
                    WHERE id=$2
                """, limit.monthly_limit, existing["id"])
            else:
                await conn.execute("""
                    INSERT INTO limits (user_id, category, monthly_limit, month, year)
                    VALUES ($1, $2, $3, $4, $5)
                """, limit.user_id, limit.category,
                     limit.monthly_limit, limit.month, limit.year)
