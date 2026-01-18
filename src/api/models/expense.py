"""Expense API models."""

from pydantic import BaseModel
from typing import Optional, List


class ExpenseCreate(BaseModel):
    """Request model for creating an expense."""

    expense: str
    amount: float
    date: Optional[str] = None  # Optional: defaults to current date if not provided


class ExpenseUpdate(BaseModel):
    """Request model for updating an expense."""

    expense: Optional[str] = None
    amount: Optional[float] = None


class ExpenseResponse(BaseModel):
    """Response model for an expense."""

    date: str
    expense: str
    amount: float
    index: int


class PaginatedExpensesResponse(BaseModel):
    """Response model for paginated expenses."""

    expenses: List[ExpenseResponse]
    total: int
    limit: int
    offset: int
    has_more: bool
    returned: int

