"""Expense management routes."""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional, List, Dict, Any
from datetime import datetime

from ..models.expense import ExpenseCreate, ExpenseUpdate, ExpenseResponse, PaginatedExpensesResponse
from ..dependencies import get_expense_service
from ...ledger.services.expense_service import ExpenseService


router = APIRouter(prefix="/expenses", tags=["expenses"])


def validate_date_format(date_str: str) -> bool:
    """Validate date string format (YYYY-MM-DD)."""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


@router.post("", response_model=Dict[str, Any])
async def create_expense(
    expense_data: ExpenseCreate,
    expense_service: ExpenseService = Depends(get_expense_service),
):
    """Add a new expense (date defaults to current date)."""
    try:
        # Validate date format if provided
        if expense_data.date and not validate_date_format(expense_data.date):
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

        expense = expense_service.add_expense(
            expense_data.expense, expense_data.amount, expense_data.date
        )

        return {
            "message": "Expense added successfully",
            "expense": {
                "date": expense.date,
                "expense": expense.expense,
                "amount": expense.amount,
            },
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding expense: {str(e)}")


@router.get("", response_model=PaginatedExpensesResponse)
async def get_expenses(
    date: Optional[str] = Query(None, description="Specific date (YYYY-MM-DD)"),
    week: Optional[bool] = Query(False, description="Get expenses for current week"),
    range: Optional[str] = Query(None, description="Date range (start_date,end_date)"),
    limit: int = Query(50, ge=1, le=1000, description="Number of expenses to return (1-1000)"),
    offset: int = Query(0, ge=0, description="Number of expenses to skip"),
    expense_service: ExpenseService = Depends(get_expense_service),
):
    """Get expenses with optional filtering and pagination."""
    try:
        # Filter expenses
        if date:
            if not validate_date_format(date):
                raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
            expenses_dict = {date: expense_service.get_expenses_by_date(date)}
        elif week:
            expenses_dict = expense_service.get_expenses_by_week()
        elif range:
            try:
                start_date, end_date = range.split(",")
                start_date = start_date.strip()
                end_date = end_date.strip()
                if not validate_date_format(start_date) or not validate_date_format(end_date):
                    raise ValueError("Invalid date format")
                expenses_dict = expense_service.get_expenses_by_range(start_date, end_date)
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
        else:
            expenses_dict = expense_service.get_all_expenses()

        # Format expenses
        all_expenses = []
        for date_key, date_expenses in expenses_dict.items():
            for index, expense in enumerate(date_expenses):
                all_expenses.append(
                    ExpenseResponse(
                        date=date_key,
                        expense=expense["expense"],
                        amount=float(expense["amount"]),
                        index=index,
                    )
                )

        # Sort by date (newest first)
        all_expenses.sort(key=lambda x: x.date, reverse=True)

        # Apply pagination
        total = len(all_expenses)
        start_idx = offset
        end_idx = offset + limit
        paginated_expenses = all_expenses[start_idx:end_idx]
        has_more = end_idx < total

        return PaginatedExpensesResponse(
            expenses=paginated_expenses,
            total=total,
            limit=limit,
            offset=offset,
            has_more=has_more,
            returned=len(paginated_expenses),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving expenses: {str(e)}")


@router.put("/{date}/{index}", response_model=Dict[str, Any])
async def update_expense(
    date: str,
    index: int,
    expense_update: ExpenseUpdate,
    expense_service: ExpenseService = Depends(get_expense_service),
):
    """Edit an expense on a specific date by index."""
    try:
        if not validate_date_format(date):
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

        if expense_update.expense is None and expense_update.amount is None:
            raise HTTPException(
                status_code=400, detail="At least one field (expense or amount) must be provided"
            )

        expense_service.update_expense(date, index, expense_update.expense, expense_update.amount)

        # Get updated expense
        expenses = expense_service.get_expenses_by_date(date)
        if index >= len(expenses):
            raise HTTPException(status_code=404, detail="Expense not found")

        updated_expense = expenses[index]

        return {
            "message": "Expense updated successfully",
            "expense": {
                "date": date,
                "expense": updated_expense["expense"],
                "amount": updated_expense["amount"],
                "index": index,
            },
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating expense: {str(e)}")


@router.delete("/{date}/{index}", response_model=Dict[str, str])
async def delete_expense_endpoint(
    date: str,
    index: int,
    expense_service: ExpenseService = Depends(get_expense_service),
):
    """Delete an expense on a specific date by index."""
    try:
        if not validate_date_format(date):
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

        expense_service.delete_expense(date, index)

        return {"message": "Expense deleted successfully"}

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting expense: {str(e)}")

