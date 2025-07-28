"""
Utility functions for the API
"""
import json
import sys
import os
from typing import Dict, List
from datetime import datetime, timedelta

# Add the parent directory to the path to import ledger functions
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ledger.ledger import LEDGER
from models import ExpenseResponse

def load_ledger_data() -> Dict:
    """Load ledger data and return as dict"""
    try:
        with open(LEDGER, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}

def format_expenses_response(data: Dict) -> List[ExpenseResponse]:
    """Convert ledger data to list of ExpenseResponse objects"""
    expenses = []
    for date, date_expenses in data.items():
        for index, expense in enumerate(date_expenses):
            expenses.append(ExpenseResponse(
                date=date,
                expense=expense["expense"],
                amount=float(expense["amount"]),
                index=index
            ))
    return expenses

def validate_date_format(date_str: str) -> bool:
    """Validate date string format (YYYY-MM-DD)"""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def get_week_dates() -> List[str]:
    """Get list of dates for current week (last 7 days)"""
    today = datetime.today()
    return [(today + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(-6, 1)]

def parse_date_range(range_str: str) -> tuple:
    """Parse date range string and return (start_date, end_date)"""
    try:
        start_date, end_date = range_str.split(",")
        if not validate_date_format(start_date) or not validate_date_format(end_date):
            raise ValueError("Invalid date format")
        return start_date.strip(), end_date.strip()
    except ValueError:
        raise ValueError("Invalid range format. Use start_date,end_date (YYYY-MM-DD,YYYY-MM-DD)")

def filter_data_by_date(data: Dict, date: str) -> Dict:
    """Filter data for a specific date"""
    return {date: data.get(date, [])}

def filter_data_by_week(data: Dict) -> Dict:
    """Filter data for current week"""
    week_dates = get_week_dates()
    return {d: data.get(d, []) for d in week_dates if d in data}

def filter_data_by_range(data: Dict, start_date: str, end_date: str) -> Dict:
    """Filter data for date range"""
    filtered_data = {}
    for d, expenses in data.items():
        if start_date <= d <= end_date:
            filtered_data[d] = expenses
    return filtered_data

def calculate_summary_stats(data: Dict, period_description: str) -> Dict:
    """Calculate summary statistics for filtered data"""
    total = 0
    all_expenses = []
    transaction_count = 0
    days_with_expenses = len([d for d in data.keys() if data[d]])
    
    for d, expenses in data.items():
        for exp in expenses:
            exp_with_date = exp.copy()
            exp_with_date["date"] = d
            all_expenses.append(exp_with_date)
            total += float(exp["amount"])
            transaction_count += 1
    
    return {
        "total": round(total, 2),
        "expenses": all_expenses,
        "period": period_description,
        "transaction_count": transaction_count,
        "days_with_expenses": days_with_expenses
    }