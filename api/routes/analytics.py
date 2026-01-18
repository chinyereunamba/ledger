"""
Analytics and summary routes
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Dict, Any
from datetime import datetime

from models import SummaryResponse, StatsResponse
from utils import (
    load_ledger_data, validate_date_format, filter_data_by_date,
    filter_data_by_week, filter_data_by_range, parse_date_range,
    calculate_summary_stats
)

# Import ledger functions
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ledger.ledger import get_expense_category

router = APIRouter(tags=["analytics"])

@router.get("/summary", response_model=Dict[str, Any])
async def get_summary_endpoint(
    date: Optional[str] = Query(None, description="Specific date (YYYY-MM-DD)"),
    week: Optional[bool] = Query(False, description="Get summary for current week"),
    range: Optional[str] = Query(None, description="Date range (start_date,end_date)")
):
    """Get expense summary with optional filtering"""
    try:
        data = load_ledger_data()
        
        if not data:
            return {
                "total": 0,
                "expenses": [],
                "period": "No data available",
                "transaction_count": 0,
                "days_with_expenses": 0
            }
        
        # Summary for specific date
        if date:
            if not validate_date_format(date):
                raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
            
            filtered_data = filter_data_by_date(data, date)
            period_description = f"Date: {date}"
        
        # Summary for current week
        elif week:
            filtered_data = filter_data_by_week(data)
            from utils import get_week_dates
            week_dates = get_week_dates()
            period_description = f"Week: {week_dates[0]} to {week_dates[-1]}"
        
        # Summary for date range
        elif range:
            try:
                start_date, end_date = parse_date_range(range)
                filtered_data = filter_data_by_range(data, start_date, end_date)
                period_description = f"Range: {start_date} to {end_date}"
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        # All-time summary
        else:
            filtered_data = data
            period_description = "All time"
        
        return calculate_summary_stats(filtered_data, period_description)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting summary: {str(e)}")

@router.get("/monthly/{month}", response_model=Dict[str, Any])
async def get_monthly_stats(month: str):
    """Get statistics for a specific month (YYYY-MM format)"""
    try:
        # Validate month format
        try:
            datetime.strptime(month, "%Y-%m")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid month format. Use YYYY-MM")
        
        data = load_ledger_data()
        
        if not data:
            return {
                "month": month,
                "total_spent": 0,
                "transaction_count": 0,
                "days_tracked": 0,
                "daily_average": 0,
                "categories": {},
                "top_expenses": []
            }
        
        # Filter data for the specific month
        month_data = {date: expenses for date, expenses in data.items() if date.startswith(month)}
        
        if not month_data:
            return {
                "month": month,
                "total_spent": 0,
                "transaction_count": 0,
                "days_tracked": 0,
                "daily_average": 0,
                "categories": {},
                "top_expenses": []
            }
        
        # Calculate month stats
        total_spent = 0
        category_totals = {}
        expense_totals = {}
        transaction_count = 0
        
        for date, expenses in month_data.items():
            for expense in expenses:
                amount = float(expense["amount"])
                expense_name = expense["expense"]
                
                total_spent += amount
                transaction_count += 1
                
                # Track category totals
                category = get_expense_category(expense_name)
                category_totals[category] = category_totals.get(category, 0) + amount
                
                # Track expense totals
                expense_totals[expense_name] = expense_totals.get(expense_name, 0) + amount
        
        days_tracked = len(month_data)
        daily_average = total_spent / days_tracked if days_tracked > 0 else 0
        
        # Top expenses
        top_expenses = sorted(expense_totals.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "month": month,
            "total_spent": round(total_spent, 2),
            "transaction_count": transaction_count,
            "days_tracked": days_tracked,
            "daily_average": round(daily_average, 2),
            "categories": {
                name: round(amount, 2) for name, amount in category_totals.items()
            },
            "top_expenses": [
                {"name": name, "amount": round(amount, 2)}
                for name, amount in top_expenses
            ]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting monthly stats: {str(e)}")

@router.get("/stats", response_model=Dict[str, Any])
async def get_stats_endpoint():
    """Get comprehensive analytics and statistics"""
    try:
        data = load_ledger_data()
        
        if not data:
            return {
                "total_spent": 0,
                "daily_average": 0,
                "transaction_count": 0,
                "days_tracked": 0,
                "most_spent_category": None,
                "most_frequent_expense": None,
                "most_expensive_day": None,
                "top_expenses": [],
                "top_categories": [],
                "category_breakdown": {}
            }
        
        # Calculate basic stats
        total_spent = 0
        expense_counts = {}
        category_totals = {}
        daily_totals = {}
        monthly_totals = {}
        monthly_category_totals = {}
        all_expenses = []
        
        for date, expenses in data.items():
            daily_total = 0
            month = date[:7]  # Extract YYYY-MM
            
            for expense in expenses:
                amount = float(expense["amount"])
                expense_name = expense["expense"]
                
                # Track totals
                total_spent += amount
                daily_total += amount
                
                # Track monthly totals
                monthly_totals[month] = monthly_totals.get(month, 0) + amount
                
                # Track expense frequency
                expense_counts[expense_name] = expense_counts.get(expense_name, 0) + 1
                
                # Track category totals (all-time)
                category = get_expense_category(expense_name)
                category_totals[category] = category_totals.get(category, 0) + amount
                
                # Track monthly category totals
                if month not in monthly_category_totals:
                    monthly_category_totals[month] = {}
                monthly_category_totals[month][category] = monthly_category_totals[month].get(category, 0) + amount
                
                all_expenses.append({
                    "date": date,
                    "expense": expense_name,
                    "amount": amount,
                    "category": category
                })
            
            daily_totals[date] = daily_total
        
        # Calculate derived stats
        days_tracked = len(data)
        transaction_count = len(all_expenses)
        daily_average = total_spent / days_tracked if days_tracked > 0 else 0
        
        # Find most spent category
        most_spent_category = max(category_totals.items(), key=lambda x: x[1]) if category_totals else (None, 0)
        
        # Find most frequent expense
        most_frequent_expense = max(expense_counts.items(), key=lambda x: x[1]) if expense_counts else (None, 0)
        
        # Find most expensive day
        most_expensive_day = max(daily_totals.items(), key=lambda x: x[1]) if daily_totals else (None, 0)
        
        # Top 5 expenses by total amount
        expense_totals = {}
        for expense in all_expenses:
            name = expense["expense"]
            expense_totals[name] = expense_totals.get(name, 0) + expense["amount"]
        
        top_expenses = sorted(expense_totals.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Top 5 categories
        top_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Get current month stats
        current_month = datetime.now().strftime("%Y-%m")
        current_month_spent = monthly_totals.get(current_month, 0)
        current_month_categories = monthly_category_totals.get(current_month, {})
        
        return {
            "total_spent": round(total_spent, 2),
            "daily_average": round(daily_average, 2),
            "transaction_count": transaction_count,
            "days_tracked": days_tracked,
            "most_spent_category": {
                "name": most_spent_category[0],
                "amount": round(most_spent_category[1], 2)
            } if most_spent_category[0] else None,
            "most_frequent_expense": {
                "name": most_frequent_expense[0],
                "count": most_frequent_expense[1]
            } if most_frequent_expense[0] else None,
            "most_expensive_day": {
                "date": most_expensive_day[0],
                "amount": round(most_expensive_day[1], 2)
            } if most_expensive_day[0] else None,
            "top_expenses": [
                {"name": name, "total_amount": round(amount, 2)}
                for name, amount in top_expenses
            ],
            "top_categories": [
                {"name": name, "total_amount": round(amount, 2)}
                for name, amount in top_categories
            ],
            "category_breakdown": {
                name: round(amount, 2) for name, amount in category_totals.items()
            },
            "monthly_spending": {
                month: round(amount, 2) for month, amount in monthly_totals.items()
            },
            "current_month_spent": round(current_month_spent, 2),
            "current_month_categories": {
                name: round(amount, 2) for name, amount in current_month_categories.items()
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")