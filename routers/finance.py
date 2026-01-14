from fastapi import APIRouter
from models.schemas import FinanceEventIn
from services.finance_service import (
    add_finance_event,
    get_finance_summary,
    get_finance_flow,
)

router = APIRouter(prefix="/api/finance")


def get_mock_user():
    return 1  # временно, DEV


@router.post("/event")
async def create_event(data: FinanceEventIn):
    user_id = get_mock_user()
    await add_finance_event(
        telegram_user_id=user_id,
        amount=data.amount,
        kind=data.kind,
        category=data.category,
        note=data.note,
    )
    return {"status": "ok"}


@router.get("/summary")
async def summary():
    user_id = get_mock_user()
    return await get_finance_summary(user_id)


@router.get("/flow")
async def flow(limit: int = 50):
    user_id = get_mock_user()
    return await get_finance_flow(user_id, limit)
