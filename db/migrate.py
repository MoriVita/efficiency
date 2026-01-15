import os
from pathlib import Path
from db.database import get_pool

MIGRATIONS_DIR = Path(__file__).parent / "migrations"


async def run_migrations():
    pool = get_pool()

    async with pool.acquire() as conn:
        # 1. ГАРАНТИРУЕМ, ЧТО schema_migrations СУЩЕСТВУЕТ
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version TEXT PRIMARY KEY,
                applied_at TIMESTAMP NOT NULL DEFAULT now()
            );
        """)

        # 2. ЧИТАЕМ УЖЕ ПРИМЕНЁННЫЕ МИГРАЦИИ
        rows = await conn.fetch("SELECT version FROM schema_migrations")
        applied = {r["version"] for r in rows}

        # 3. ПРИМЕНЯЕМ НОВЫЕ
        for file in sorted(MIGRATIONS_DIR.glob("*.sql")):
            version = file.stem

            if version in applied:
                continue

            print(f"[migrate] applying {file.name}")

            sql = file.read_text(encoding="utf-8")
            await conn.execute(sql)

        print("[migrate] all migrations applied")
