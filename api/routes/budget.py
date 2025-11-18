"""
Budget management routes
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any
from datetime import datetime
import json
import os
from pathlib import Path

router = APIRouter(prefix="/budget", tags=["budget"])

def get_data_dir():
    """Get the data directory path"""
    return Path("../data")

def load_budget_data():
    """Load budget data from JSON file"""
    data_dir = get_data_dir()
    budget_file = data_dir / "budget.json"
    
    if not budget_file.exists():
        # Create default budget structure
        default_data = {
            "monthly_budgets": {},
            "auto_reset": True,
            "current_month": get_current_month()
        }
        data_dir.mkdir(exist_ok=True)
        with open(budget_file, 'w') as f:
            json.dump(default_data, f, indent=2)
        return default_data
    
    with open(budget_file, 'r') as f:
        return json.load(f)

def save_budget_data(data):
    """Save budget data to JSON file"""
    data_dir = get_data_dir()
    budget_file = data_dir / "budget.json"
    data_dir.mkdir(exist_ok=True)
    
    with open(budget_file, 'w') as f:
        json.dump(data, f, indent=2)

def load_ledger_data():
    """Load ledger data to calculate spending"""
    data_dir = get_data_dir()
    ledger_file = data_dir / "ledger.json"
    
    if not ledger_file.exists():
        return {}
    
    with open(ledger_file, 'r') as f:
        return json.load(f)

def get_current_month():
    """Get current month in YYYY-MM format"""
    return datetime.now().strftime("%Y-%m")

def reset_monthly_budget_if_needed():
    """Reset budget for new month if auto-reset is enabled"""
    budget_data = load_budget_data()
    current_month = get_current_month()
    
    # Check if we need to reset for a new month
    if budget_data.get("auto_reset", True) and budget_data.get("current_month") != current_month:
        # Check if we have previous month's budget to copy the amount (but not expenses)
        if budget_data["monthly_budgets"]:
            # Get the last month's budget amount
            last_month_budgets = budget_data["monthly_budgets"]
            if last_month_budgets:
                # Get the most recent budget amount
                recent_budget = list(last_month_budgets.values())[-1].get("amount", 0)
                
                # Set budget for current month - start fresh with 0 spent
                budget_data["monthly_budgets"][current_month] = {
                    "amount": recent_budget,
                    "spent": 0,  # Always start fresh each month
                    "created_at": datetime.now().isoformat(),
                    "reset_from_previous": True
                }
        
        budget_data["current_month"] = current_month
        save_budget_data(budget_data)
    
    return budget_data

@router.get("", response_model=Dict[str, Any])
async def get_budget():
    """Get current month's budget information"""
    try:
        budget_data = reset_monthly_budget_if_needed()
        current_month = get_current_month()
        
        # Get current month's budget
        monthly_budget = budget_data["monthly_budgets"].get(current_month, {
            "amount": 0,
            "spent": 0,
            "created_at": None,
            "reset_from_previous": False
        })
        
        # Calculate current month's spending from ledger (only current month)
        ledger_data = load_ledger_data()
        current_spending = 0
        
        for date_str, expenses in ledger_data.items():
            if date_str.startswith(current_month):
                for expense in expenses:
                    current_spending += float(expense["amount"])
        
        # Update spent amount in budget data (only current month's expenses)
        monthly_budget["spent"] = current_spending
        budget_data["monthly_budgets"][current_month] = monthly_budget
        save_budget_data(budget_data)
        
        # Calculate remaining and percentage
        budget_amount = monthly_budget["amount"]
        remaining = budget_amount - current_spending
        percentage = (current_spending / budget_amount * 100) if budget_amount > 0 else 0
        
        return {
            "month": current_month,
            "budget_amount": budget_amount,
            "spent": current_spending,
            "remaining": remaining,
            "percentage": min(percentage, 100),
            "over_budget": current_spending > budget_amount,
            "auto_reset": budget_data.get("auto_reset", True),
            "created_at": monthly_budget.get("created_at"),
            "reset_from_previous": monthly_budget.get("reset_from_previous", False)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting budget: {str(e)}")

@router.post("", response_model=Dict[str, Any])
async def set_budget(amount: float = Query(..., description="Monthly budget amount")):
    """Set budget for current month"""
    try:
        if amount < 0:
            raise HTTPException(status_code=400, detail="Budget amount must be positive")
        
        budget_data = reset_monthly_budget_if_needed()
        current_month = get_current_month()
        
        # Calculate current month's spending only (fresh start each month)
        ledger_data = load_ledger_data()
        current_spending = 0
        
        for date_str, expenses in ledger_data.items():
            if date_str.startswith(current_month):
                for expense in expenses:
                    current_spending += float(expense["amount"])
        
        # Set budget for current month - only track current month's expenses
        budget_data["monthly_budgets"][current_month] = {
            "amount": amount,
            "spent": current_spending,  # Only current month's expenses
            "created_at": datetime.now().isoformat(),
            "reset_from_previous": False
        }
        
        save_budget_data(budget_data)
        
        return {
            "message": "Budget set successfully",
            "month": current_month,
            "budget_amount": amount,
            "spent": current_spending,
            "remaining": amount - current_spending
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error setting budget: {str(e)}")

@router.put("/auto-reset", response_model=Dict[str, Any])
async def toggle_auto_reset(enabled: bool = Query(..., description="Enable/disable automatic monthly budget reset")):
    """Toggle automatic monthly budget reset"""
    try:
        budget_data = load_budget_data()
        budget_data["auto_reset"] = enabled
        save_budget_data(budget_data)
        
        return {
            "message": f"Auto-reset {'enabled' if enabled else 'disabled'} successfully",
            "auto_reset": enabled
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error toggling auto-reset: {str(e)}")

@router.get("/history", response_model=Dict[str, Any])
async def get_budget_history():
    """Get budget history for all months"""
    try:
        budget_data = load_budget_data()
        ledger_data = load_ledger_data()
        
        # Calculate spending for each month that has budget data
        history = []
        
        for month, budget_info in budget_data["monthly_budgets"].items():
            # Calculate actual spending for this month
            month_spending = 0
            for date_str, expenses in ledger_data.items():
                if date_str.startswith(month):
                    for expense in expenses:
                        month_spending += float(expense["amount"])
            
            history.append({
                "month": month,
                "budget_amount": budget_info["amount"],
                "spent": month_spending,
                "remaining": budget_info["amount"] - month_spending,
                "percentage": (month_spending / budget_info["amount"] * 100) if budget_info["amount"] > 0 else 0,
                "over_budget": month_spending > budget_info["amount"],
                "created_at": budget_info.get("created_at"),
                "reset_from_previous": budget_info.get("reset_from_previous", False)
            })
        
        # Sort by month (newest first)
        history.sort(key=lambda x: x["month"], reverse=True)
        
        return {
            "history": history,
            "auto_reset": budget_data.get("auto_reset", True),
            "current_month": get_current_month()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting budget history: {str(e)}")

@router.delete("", response_model=Dict[str, str])
async def delete_current_budget():
    """Delete current month's budget"""
    try:
        budget_data = load_budget_data()
        current_month = get_current_month()
        
        if current_month in budget_data["monthly_budgets"]:
            del budget_data["monthly_budgets"][current_month]
            save_budget_data(budget_data)
            return {"message": "Current month's budget deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="No budget found for current month")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting budget: {str(e)}")