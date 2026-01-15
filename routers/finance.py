from fastapi import APIRouter, Request, HTTPException, Query
from datetime import date
from core.auth import get_current_user_id
from models.schemas import FinanceEventIn, CapitalOut
from services.finance_service import (
    create_event, get_capital, get_flow, get_day
)

router = APIRouter(prefix="/api/finance", tags=["finance"])


@router.post("/events")
async def add_event(data: FinanceEventIn, request: Request):
    user_id = await get_current_user_id(request)
    try:
        await create_event(
            user_id=user_id,
            kind=data.kind,
            amount=data.amount,
            category_id=data.category_id,
            event_date=data.date
        )
        return {"status": "ok"}
    except (ValueError, PermissionError) as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/capital", response_model=CapitalOut)
async def capital(request: Request):
    user_id = await get_current_user_id(request)
    total = await get_capital(user_id)
    return {"total": total}


@router.get("/flow")
async def flow(
    request: Request,
    start: date = Query(...),
    end: date = Query(...)
):
    user_id = await get_current_user_id(request)
    return await get_flow(user_id, start, end)


@router.get("/day")
async def day_view(request: Request, date: date):
    user_id = await get_current_user_id(request)
    return await get_day(user_id, date)
