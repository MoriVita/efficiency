from db.database import get_pool
from datetime import datetime, time, date





VALID_KINDS = {"income", "expense", "save", "invest", "withdraw"}

NEGATIVE_KINDS = {"expense", "withdraw"}


async def create_event(
    user_id: int,
    kind: str,
    amount: int,
    category_id: int | None,
    event_date: date | None
):
    if kind not in VALID_KINDS:
        raise ValueError("Invalid event kind")

    if amount <= 0:
        raise ValueError("Amount must be positive")

    signed_amount = -amount if kind in NEGATIVE_KINDS else amount
    occurred_at = (
        datetime.combine(event_date, time.min)
        if event_date
        else datetime.utcnow()
    )

    pool = get_pool()
    async with pool.acquire() as conn:
        if category_id:
            exists = await conn.fetchval("""
                SELECT 1 FROM categories
                WHERE id = $1 AND user_id = $2
            """, category_id, user_id)

            if not exists:
                raise PermissionError("Category not found")

        await conn.execute("""
            INSERT INTO finance_events_v2
            (user_id, category_id, kind, amount, occurred_at)
            VALUES ($1, $2, $3, $4, $5)
        """, user_id, category_id, kind, signed_amount, occurred_at)


async def get_capital(user_id: int) -> int:
    pool = get_pool()
    async with pool.acquire() as conn:
        return await conn.fetchval("""
            SELECT COALESCE(SUM(amount), 0)
            FROM finance_events_v2
            WHERE user_id = $1
        """, user_id)


async def get_flow(user_id: int, date_from, date_to):
    pool = get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT
                DATE(occurred_at) as day,
                SUM(amount) as net,
                json_agg(json_build_object(
                    'id', id,
                    'kind', kind,
                    'amount', amount,
                    'category_id', category_id
                ) ORDER BY occurred_at) as events
            FROM finance_events_v2
            WHERE user_id = $1
              AND occurred_at BETWEEN $2 AND $3
            GROUP BY day
            ORDER BY day DESC
        """, user_id, date_from, date_to)

        return [dict(r) for r in rows]


async def get_day(user_id: int, day: date):
    pool = get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT id, kind, amount, category_id
            FROM finance_events_v2
            WHERE user_id = $1
              AND DATE(occurred_at) = $2
            ORDER BY occurred_at
        """, user_id, day)

        net = sum(r["amount"] for r in rows)

        return {
            "date": day,
            "net": net,
            "events": [dict(r) for r in rows]
        }



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
