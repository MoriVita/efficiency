from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from pathlib import Path

router = APIRouter()
BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES = BASE_DIR / "templates"


@router.get("/", response_class=HTMLResponse)
async def index():
    return (TEMPLATES / "index.html").read_text(encoding="utf-8")


@router.get("/profile", response_class=HTMLResponse)
async def profile():
    return (TEMPLATES / "profile.html").read_text(encoding="utf-8")


@router.get("/finance", response_class=HTMLResponse)
async def finance():
    return (TEMPLATES / "finance.html").read_text(encoding="utf-8")
