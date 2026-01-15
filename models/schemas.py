from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date



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


class FinanceEventIn(BaseModel):
    kind: str              # income | expense | save | invest | withdraw
    amount: int
    category_id: Optional[int] = None
    date: Optional[date] = None


class CapitalOut(BaseModel):
    total: int