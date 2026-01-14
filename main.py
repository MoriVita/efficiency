from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
load_dotenv()

from db.database import init_db, close_db
from db.migrate import run_migrations
from routers import pages, finance, limits



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(pages.router)
app.include_router(finance.router)
app.include_router(limits.router)


@app.on_event("startup")
async def startup():
    await init_db()
    await run_migrations()

@app.on_event("shutdown")
async def shutdown():
    await close_db()
