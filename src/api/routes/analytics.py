"""Analytics and summary routes."""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional, Dict, Any
from datetime import datetime

from ..models.analytics import SummaryResponse, StatsResponse
from ..dependencies import get_analytics_service, get_expense_service
from ...ledger.services import AnalyticsService, ExpenseService


router = APIRouter(tags=["analytics"])


def validate_date_format(date_str: str) -> bool:
    """Validate date string format (YYYY-MM-DD)."""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


@router.get("/summary", response_model=Dict[str, Any])
async def get_summary_endpoint(
    date: Optional[str] = Query(None, description="Specific date (YYYY-MM-DD)"),
    week: Optional[bool] = Query(False, description="Get summary for current week"),
    range: Optional[str] = Query(None, description="Date range (start_date,end_date)"),
    analytics_service: AnalyticsService = Depends(get_analytics_service),
    expense_service: ExpenseService = Depends(get_expense_service),
):
    """Get expense summary with optional filtering."""
    try:
        # Get filtered expenses
        if date:
            if not validate_date_format(date):
                raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
            expenses_dict = {date: expense_service.get_expenses_by_date(date)}
            period_description = f"Date: {date}"
        elif week:
            expenses_dict = expense_service.get_expenses_by_week()
            from datetime import timedelta
            today = datetime.today()
            week_start = (today + timedelta(days=-6)).strftime("%Y-%m-%d")
            week_end = today.strftime("%Y-%m-%d")
            period_description = f"Week: {week_start} to {week_end}"
        elif range:
            try:
                start_date, end_date = range.split(",")
                start_date = start_date.strip()
                end_date = end_date.strip()
                if not validate_date_format(start_date) or not validate_date_format(end_date):
                    raise ValueError("Invalid date format")
                expenses_dict = expense_service.get_expenses_by_range(start_date, end_date)
                period_description = f"Range: {start_date} to {end_date}"
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
        else:
            expenses_dict = expense_service.get_all_expenses()
            period_description = "All time"

        return analytics_service.calculate_summary_stats(expenses_dict, period_description)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting summary: {str(e)}")


@router.get("/monthly/{month}", response_model=Dict[str, Any])
async def get_monthly_stats(
    month: str,
    analytics_service: AnalyticsService = Depends(get_analytics_service),
):
    """Get statistics for a specific month (YYYY-MM format)."""
    try:
        # Validate month format
        try:
            datetime.strptime(month, "%Y-%m")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid month format. Use YYYY-MM")

        return analytics_service.get_monthly_stats(month)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting monthly stats: {str(e)}")


@router.get("/stats", response_model=Dict[str, Any])
async def get_stats_endpoint(
    analytics_service: AnalyticsService = Depends(get_analytics_service),
):
    """Get comprehensive analytics and statistics."""
    try:
        return analytics_service.calculate_comprehensive_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")

