from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from psycopg2.pool import SimpleConnectionPool
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from fastapi import Query
from psycopg2.extras import RealDictCursor



load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES = BASE_DIR / "templates"

app = FastAPI()



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)



pool = SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    host = os.getenv("DB_HOST"),
    database = os.getenv("DB_NAME"),
    user = os.getenv("DB_USER"),
    password = os.getenv("DB_PASSWORD")

)



class FinanceEntry(BaseModel):
    amount: int
    category: str
    impact: str


class LimitIn(BaseModel):
    category: str
    monthly_limit: int
    month: int
    year: int
    user_id: int


@app.get("/", response_class=HTMLResponse)
def index():
    return (TEMPLATES / "index.html").read_text(encoding="utf-8")



@app.get("/profile", response_class=HTMLResponse)
def profile():
    return (TEMPLATES / "profile.html").read_text(encoding="utf-8")



@app.get("/finance", response_class=HTMLResponse)
def finance():
    return (TEMPLATES / "finance.html").read_text(encoding="utf-8")



@app.get("/metrics")
def metrics():
    return {"productivity_score": 82}



def get_user_expenses(user_id: int):
    conn = pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM expenses WHERE user_id = %s",
                (user_id,)
            )
            return cur.fetchall()
    finally:
        pool.putconn(conn)

@app.get("/api/finance/summary")
def finance_summary(user_id: int):
    conn = pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    SUM(CASE WHEN type='save' THEN amount ELSE 0 END) AS saved,
                    SUM(CASE WHEN type='invest' THEN amount ELSE 0 END) AS invested,
                    SUM(CASE WHEN type='expense' THEN amount ELSE 0 END) AS spent
                FROM expenses
                WHERE user_id = %s
            """, (user_id,))
            row = cur.fetchone()

            return {
                "saved": row[0] or 0,
                "invested": row[1] or 0,
                "spent": row[2] or 0
            }
    finally:
        pool.putconn(conn)

# @app.get("/api/user/data")
# def get_all_data():
#     conn = pool.getconn()
#     try:
#         with conn.cursor(cursor_factory=RealDictCursor) as cur:
#             cur.execute("""
#                 SELECT id, user_id, category, monthly_limit, month, year
#                 FROM limits
#             """)
#             return cur.fetchall()
#     finally:
#         pool.putconn(conn)

@app.get("/api/user/data")
def get_data(
    user_id: int | None = Query(None),
    category: str | None = Query(None),
    month: int | None = Query(None),
    year: int | None = Query(None),
    monthly_limit: int | None = Query(None),
):
    conn = pool.getconn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            query = "SELECT * FROM limits WHERE 1=1"
            params = []

            if user_id is not None:
                query += " AND user_id = %s"
                params.append(user_id)
            if category is not None:
                query += " AND category = %s"
                params.append(category)
            if month is not None:
                query += " AND month = %s"
                params.append(month)
            if year is not None:
                query += " AND year = %s"
                params.append(year)
            if monthly_limit is not None:
                query += " AND monthly_limit = %s"
                params.append(monthly_limit)

            cur.execute(query, tuple(params))
            return cur.fetchall()
    finally:
        pool.putconn(conn)



# @app.get("/api/user/data")
# def user_data(
#         user_id: int = Query(...),
#         category: str = Query(...),
#         month: int = Query(...),
#         year: int = Query(...)
# ):
#     conn = pool.getconn()
#     try:
#         with conn.cursor() as cur:
#             cur.execute("""
#                SELECT id FROM limits
#                 WHERE user_id = %s
#                   AND category = %s
#                   AND month = %s
#                   AND year = %s
#             """,
#                 (user_id, category, month, year)
#             )
#
#             rows = cur.fetchall()
#             return rows
#
#     finally:
#         pool.putconn(conn)

@app.post("/api/limits")
def save_limit(limit: LimitIn):
    conn = pool.getconn()
    try:
        with conn.cursor() as cur:
            # проверяем: есть ли уже такой лимит
            cur.execute("""
                SELECT id FROM limits
                WHERE user_id = %s
                  AND category = %s
                  AND month = %s
                  AND year = %s
            """, (
                limit.user_id,
                limit.category,
                limit.month,
                limit.year
            ))

            existing = cur.fetchone()

            if existing:
                # обновляем
                cur.execute("""
                    UPDATE limits
                    SET monthly_limit = %s
                    WHERE id = %s
                """, (limit.monthly_limit, existing[0]))
            else:
                # создаём новый
                cur.execute("""
                    INSERT INTO limits (user_id, category, monthly_limit, month, year)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    limit.user_id,
                    limit.category,
                    limit.monthly_limit,
                    limit.month,
                    limit.year
                ))

            conn.commit()
            return {"status": "ok"}

    finally:
        pool.putconn(conn)


