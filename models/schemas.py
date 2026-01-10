from pydantic import BaseModel


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
