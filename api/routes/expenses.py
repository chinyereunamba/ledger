"""
Expense management routes
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any
from datetime import datetime
import json

from models import ExpenseCreate, ExpenseUpdate, ExpenseResponse, PaginatedExpensesResponse
from utils import (
    load_ledger_data, format_expenses_response, validate_date_format,
    filter_data_by_date, filter_data_by_week, filter_data_by_range,
    parse_date_range
)

# Import ledger functions
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ledger.ledger import add_expense, edit_expense, delete_expense, LEDGER

router = APIRouter(prefix="/expenses", tags=["expenses"])

@router.post("", response_model=Dict[str, Any])
async def create_expense(expense_data: ExpenseCreate):
    """Add a new expense (date defaults to current date)"""
    try:
        # Always use current date unless a specific date is provided and valid
        if expense_data.date:
            # Validate date format if provided
            if not validate_date_format(expense_data.date):
                raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
            date_key = expense_data.date
        else:
            # Default to current date
            date_key = datetime.now().strftime("%Y-%m-%d")
        
        # Create expense item
        expense_item = {
            "expense": expense_data.expense,
            "amount": expense_data.amount,
        }
        
        # Load existing data
        data = load_ledger_data()
        
        # Add expense under the date
        if date_key not in data:
            data[date_key] = []
        
        data[date_key].append(expense_item)
        
        # Save back to file
        with open(LEDGER, "w") as f:
            json.dump(data, f, indent=2)
        
        return {
            "message": "Expense added successfully",
            "expense": {
                "date": date_key,
                "expense": expense_data.expense,
                "amount": expense_data.amount
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding expense: {str(e)}")

@router.get("", response_model=PaginatedExpensesResponse)
async def get_expenses(
    date: Optional[str] = Query(None, description="Specific date (YYYY-MM-DD)"),
    week: Optional[bool] = Query(False, description="Get expenses for current week"),
    range: Optional[str] = Query(None, description="Date range (start_date,end_date)"),
    limit: int = Query(50, ge=1, le=1000, description="Number of expenses to return (1-1000)"),
    offset: int = Query(0, ge=0, description="Number of expenses to skip")
):
    """Get expenses with optional filtering and pagination"""
    try:
        data = load_ledger_data()
        
        if not data:
            return {
                "expenses": [],
                "total": 0,
                "limit": limit,
                "offset": offset,
                "has_more": False
            }
        
        # Filter by date
        if date:
            if not validate_date_format(date):
                raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
            filtered_data = filter_data_by_date(data, date)
        
        # Filter by week
        elif week:
            filtered_data = filter_data_by_week(data)
        
        # Filter by range
        elif range:
            try:
                start_date, end_date = parse_date_range(range)
                filtered_data = filter_data_by_range(data, start_date, end_date)
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        # No filter - return all
        else:
            filtered_data = data
        
        # Get all expenses and sort by date (newest first)
        all_expenses = format_expenses_response(filtered_data)
        all_expenses.sort(key=lambda x: x.date, reverse=True)
        
        # Calculate pagination
        total = len(all_expenses)
        start_idx = offset
        end_idx = offset + limit
        
        # Apply pagination
        paginated_expenses = all_expenses[start_idx:end_idx]
        has_more = end_idx < total
        
        return {
            "expenses": [expense.dict() for expense in paginated_expenses],
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": has_more,
            "returned": len(paginated_expenses)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving expenses: {str(e)}")

@router.put("/{date}/{index}", response_model=Dict[str, Any])
async def update_expense(date: str, index: int, expense_update: ExpenseUpdate):
    """Edit an expense on a specific date by index"""
    try:
        # Validate date format
        if not validate_date_format(date):
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        
        # Validate that at least one field is being updated
        if expense_update.expense is None and expense_update.amount is None:
            raise HTTPException(status_code=400, detail="At least one field (expense or amount) must be provided")
        
        # Check if expense exists before update
        data = load_ledger_data()
        if date not in data or index >= len(data[date]) or index < 0:
            raise HTTPException(status_code=404, detail="Expense not found")
        
        # Use the existing edit_expense function
        edit_expense(date, index, expense_update.expense, expense_update.amount)
        
        # Get the updated expense to return
        data = load_ledger_data()
        updated_expense = data[date][index]
        
        return {
            "message": "Expense updated successfully",
            "expense": {
                "date": date,
                "expense": updated_expense["expense"],
                "amount": updated_expense["amount"],
                "index": index
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating expense: {str(e)}")

@router.delete("/{date}/{index}", response_model=Dict[str, str])
async def delete_expense_endpoint(date: str, index: int):
    """Delete an expense on a specific date by index"""
    try:
        # Validate date format
        if not validate_date_format(date):
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        
        # Check if expense exists before deletion
        data = load_ledger_data()
        if date not in data or index >= len(data[date]) or index < 0:
            raise HTTPException(status_code=404, detail="Expense not found")
        
        # Use the existing delete_expense function
        delete_expense(date, index)
        
        return {"message": "Expense deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting expense: {str(e)}")