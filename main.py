from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from psycopg2.pool import SimpleConnectionPool


BASE_DIR = Path(__file__).resolve().parent
TEMPLATES = BASE_DIR / "templates"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

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
from pydantic import BaseModel

class FinanceEntry(BaseModel):
    amount: int
    category: str
    impact: str


@app.post("/api/finance/add")
def add_finance(entry: FinanceEntry):
    print("💰 NEW FINANCE ENTRY")
    print(entry)

    # ПОКА ЧТО: заглушка
    # Потом здесь будет БД, аналитика, ИИ

    return {
        "status": "ok",
        "entry": entry
    }








pool = SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    host="localhost",
    database="test_db",
    user="macbook",
    password=""
)


def get_all_students_from_db():
    conn = pool.getconn()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, last_name, grade FROM students")
            return cursor.fetchall()
    finally:
        pool.putconn(conn)



@app.get("/api/students")
def get_students():
    students = get_all_students_from_db()

    # превращаем в JSON-удобный формат
    return [
        {
            "id": s[0],
            "last_name": s[1],
            "grade": s[2]
        }
        for s in students
    ]
