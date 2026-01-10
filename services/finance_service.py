from db.database import get_pool


async def get_finance_summary(user_id: int):
    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
            SELECT
                SUM(CASE WHEN type='save' THEN amount ELSE 0 END) AS saved,
                SUM(CASE WHEN type='invest' THEN amount ELSE 0 END) AS invested,
                SUM(CASE WHEN type='expense' THEN amount ELSE 0 END) AS spent
            FROM expenses
            WHERE user_id = $1
        """, user_id)

        return {
            "saved": row["saved"] or 0,
            "invested": row["invested"] or 0,
            "spent": row["spent"] or 0
        }
