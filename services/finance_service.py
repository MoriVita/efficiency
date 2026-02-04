from db.database import get_pool
from datetime import datetime, time, date
from typing import Any
import json




VALID_KINDS = {"income", "expense", "save", "invest"}

NEGATIVE_KINDS = {"expense"}


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

#добавить в "зафиксировать действие"
async def get_flow(user_id: int, date_from, date_to):
    pool = get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT
                DATE(occurred_at) as day,
                SUM(amount) as net,
                json_agg(
                    json_build_object(
                        'id', id,
                        'kind', kind,
                        'amount', amount,
                        'category_id', category_id
                    )
                    ORDER BY occurred_at
                )::jsonb as events
            FROM finance_events_v2
            WHERE user_id = $1
              AND occurred_at BETWEEN $2 AND $3
            GROUP BY day
            ORDER BY day DESC
        """, user_id, date_from, date_to)


        result = []
        for r in rows:
            d = dict(r)


            if isinstance(d["events"], str):
                d["events"] = json.loads(d["events"])

            result.append(d)

        return result

async def get_category_limits(user_id: int):
    pool = get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT
                cl.id,
                c.name AS category,
                cl.monthly_limit,
                cl.month,
                cl.year
            FROM category_limits cl
            JOIN categories c ON c.id = cl.category_id
            WHERE cl.user_id = $1
            ORDER BY cl.year DESC, cl.month DESC
        """, user_id)

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





