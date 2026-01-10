from fastapi import APIRouter
from services.finance_service import get_finance_summary

router = APIRouter(prefix="/api/finance")


@router.get("/summary")
async def finance_summary(user_id: int):
    return await get_finance_summary(user_id)
