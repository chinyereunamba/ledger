"""
Pydantic models for request/response validation
"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class ExpenseCreate(BaseModel):
    expense: str
    amount: float
    date: Optional[str] = None  # Optional: defaults to current date if not provided

class ExpenseUpdate(BaseModel):
    expense: Optional[str] = None
    amount: Optional[float] = None

class ExpenseResponse(BaseModel):
    date: str
    expense: str
    amount: float
    index: int

class PaginatedExpensesResponse(BaseModel):
    expenses: List[ExpenseResponse]
    total: int
    limit: int
    offset: int
    has_more: bool
    returned: int

class SummaryResponse(BaseModel):
    total: float
    expenses: List[Dict[str, Any]]
    period: str
    transaction_count: int
    days_with_expenses: Optional[int] = None

class CategoryInfo(BaseModel):
    name: str
    amount: float

class ExpenseInfo(BaseModel):
    name: str
    total_amount: Optional[float] = None
    count: Optional[int] = None

class DayInfo(BaseModel):
    date: str
    amount: float

class StatsResponse(BaseModel):
    total_spent: float
    daily_average: float
    transaction_count: int
    days_tracked: int
    most_spent_category: Optional[CategoryInfo] = None
    most_frequent_expense: Optional[ExpenseInfo] = None
    most_expensive_day: Optional[DayInfo] = None
    top_expenses: List[ExpenseInfo]
    top_categories: List[CategoryInfo]
    category_breakdown: Dict[str, float]

class HealthResponse(BaseModel):
    status: str
    message: str

class APIInfoResponse(BaseModel):
    message: str
    version: str
    endpoints: Dict[str, Dict[str, str]]
    filters: Dict[str, str]