from db.database import get_pool


async def add_finance_event(
    telegram_user_id: int,
    amount: int,
    kind: str,
    category: str | None = None,
    note: str | None = None,
):
    pool = get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO finance_events (telegram_user_id, amount, kind, category, note)
            VALUES ($1, $2, $3, $4, $5)
            """,
            telegram_user_id,
            amount,
            kind,
            category,
            note,
        )


async def get_finance_summary(telegram_user_id: int):
    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT
                SUM(CASE WHEN kind='save' THEN amount ELSE 0 END) AS saved,
                SUM(CASE WHEN kind='invest' THEN amount ELSE 0 END) AS invested,
                SUM(CASE WHEN kind='expense' THEN amount ELSE 0 END) AS spent
            FROM finance_events
            WHERE telegram_user_id = $1
            """,
            telegram_user_id,
        )

        saved = row["saved"] or 0
        invested = row["invested"] or 0
        spent = row["spent"] or 0

        return {
            "saved": saved,
            "invested": invested,
            "spent": spent,
            "net": saved + invested - spent,
        }


async def get_finance_flow(telegram_user_id: int, limit: int = 50):
    pool = get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT ts, amount, kind, category
            FROM finance_events
            WHERE telegram_user_id = $1
            ORDER BY ts DESC
            LIMIT $2
            """,
            telegram_user_id,
            limit,
        )

        return [dict(row) for row in rows]
