from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
load_dotenv()
from contextlib import asynccontextmanager

from db.database import init_db, close_db
from db.migrate import run_migrations
from routers import pages, finance, limits, categories, goals




@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await run_migrations()
    yield
    await close_db()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(pages.router)
app.include_router(finance.router)
app.include_router(limits.router)
app.include_router(categories.router)
app.include_router(goals.router)