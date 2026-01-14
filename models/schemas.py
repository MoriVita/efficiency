from pydantic import BaseModel
from typing import Optional
from datetime import datetime


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

class FinanceEventIn(BaseModel):
    amount: int
    kind: str  # save | invest | expense
    category: Optional[str] = None
    note: Optional[str] = None


class FinanceEventOut(BaseModel):
    ts: datetime
    amount: int
    kind: str
    category: Optional[str]