"""Analytics API models."""

from pydantic import BaseModel
from typing import List, Dict, Optional, Any


class SummaryResponse(BaseModel):
    """Response model for expense summary."""

    total: float
    expenses: List[Dict[str, Any]]
    period: str
    transaction_count: int
    days_with_expenses: Optional[int] = None


class StatsResponse(BaseModel):
    """Response model for comprehensive statistics."""

    total_spent: float
    daily_average: float
    transaction_count: int
    days_tracked: int
    most_spent_category: Optional[Dict[str, Any]] = None
    most_frequent_expense: Optional[Dict[str, Any]] = None
    most_expensive_day: Optional[Dict[str, Any]] = None
    top_expenses: List[Dict[str, Any]]
    top_categories: List[Dict[str, Any]]
    category_breakdown: Dict[str, float]
    monthly_spending: Optional[Dict[str, float]] = None
    current_month_spent: Optional[float] = None

