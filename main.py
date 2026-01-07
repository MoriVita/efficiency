from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from psycopg2.pool import SimpleConnectionPool
import os
from dotenv import load_dotenv
from pydantic import BaseModel



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



@app.post("/api/finance/add")
def add_finance(entry: FinanceEntry):
    print("💰 NEW FINANCE ENTRY")
    print(entry)

    return {
        "status": "ok",
        "entry": entry
    }



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


# def get_all_students_from_db():
#     conn = pool.getconn()
#     try:
#         with conn.cursor() as cursor:
#             cursor.execute("SELECT id, last_name, grade FROM students")
#             return cursor.fetchall()
#     finally:
#         pool.putconn(conn)
#
#
#
# @app.get("/api/students")
# def get_students():
#     students = get_all_students_from_db()
#
#     # превращаем в JSON-удобный формат
#     return [
#         {
#             "id": s[0],
#             "last_name": s[1],
#             "grade": s[2]
#         }
#         for s in students
#     ]
