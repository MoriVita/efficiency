from fastapi import APIRouter, Query
from models.schemas import LimitIn
from services.limits_service import get_limits, save_limit

router = APIRouter(prefix="/api")


@router.get("/user/data")
async def get_data(
    user_id: int | None = Query(None),
    category: str | None = Query(None),
    month: int | None = Query(None),
    year: int | None = Query(None),
    monthly_limit: int | None = Query(None),
):
    filters = {
        k: v for k, v in locals().items() if v is not None
    }
    return await get_limits(filters)


@router.post("/limits")
async def create_limit(limit: LimitIn):
    await save_limit(limit)
    return {"status": "ok"}
