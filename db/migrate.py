from db.database import DATABASE_URL
import asyncpg
from pathlib import Path




MIGRATIONS_DIR = Path(__file__).parent / "migrations"


async def run_migrations():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not set")

    conn = await asyncpg.connect(DATABASE_URL)

    try:
        # 1. гарантируем таблицу миграций
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version TEXT PRIMARY KEY,
                applied_at TIMESTAMP DEFAULT now()
            );
        """)

        # 2. уже применённые миграции
        rows = await conn.fetch("SELECT version FROM schema_migrations;")
        applied = {row["version"] for row in rows}

        # 3. все sql-файлы
        migration_files = sorted(
            f for f in MIGRATIONS_DIR.iterdir()
            if f.suffix == ".sql"
        )

        for file in migration_files:
            version = file.stem.split("_")[0]

            if version in applied:
                continue

            print(f"[migrate] applying {file.name}")

            sql = file.read_text(encoding="utf-8")
            await conn.execute(sql)

        print("[migrate] all migrations applied")

    finally:
        await conn.close()
