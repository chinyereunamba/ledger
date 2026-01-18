"""Budget API models."""

from pydantic import BaseModel
from typing import List, Dict, Optional


class BudgetResponse(BaseModel):
    """Response model for budget status."""

    month: str
    budget_amount: float
    spent: float
    remaining: float
    percentage: float
    over_budget: bool
    auto_reset: bool
    created_at: Optional[str] = None
    reset_from_previous: bool = False


class BudgetHistoryResponse(BaseModel):
    """Response model for budget history."""

    history: List[Dict[str, Any]]
    auto_reset: bool
    current_month: str

