"""Budget management routes."""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Dict, Any

from ..models.budget import BudgetResponse, BudgetHistoryResponse
from ..dependencies import get_budget_service
from ...ledger.services.budget_service import BudgetService


router = APIRouter(prefix="/budget", tags=["budget"])


@router.get("", response_model=Dict[str, Any])
async def get_budget(
    budget_service: BudgetService = Depends(get_budget_service),
):
    """Get current month's budget information."""
    try:
        monthly_budget = budget_service.get_budget_status()

        return {
            "month": monthly_budget.month,
            "budget_amount": monthly_budget.amount,
            "spent": monthly_budget.spent,
            "remaining": monthly_budget.remaining,
            "percentage": monthly_budget.percentage_used,
            "over_budget": monthly_budget.is_over_budget,
            "auto_reset": budget_service.budget_repo.load().auto_reset,
            "created_at": monthly_budget.created_at,
            "reset_from_previous": monthly_budget.reset_from_previous,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting budget: {str(e)}")


@router.post("", response_model=Dict[str, Any])
async def set_budget(
    amount: float = Query(..., description="Monthly budget amount"),
    budget_service: BudgetService = Depends(get_budget_service),
):
    """Set budget for current month."""
    try:
        if amount < 0:
            raise HTTPException(status_code=400, detail="Budget amount must be positive")

        monthly_budget = budget_service.set_monthly_budget(amount)

        return {
            "message": "Budget set successfully",
            "month": monthly_budget.month,
            "budget_amount": monthly_budget.amount,
            "spent": monthly_budget.spent,
            "remaining": monthly_budget.remaining,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error setting budget: {str(e)}")


@router.put("/auto-reset", response_model=Dict[str, Any])
async def toggle_auto_reset(
    enabled: bool = Query(..., description="Enable/disable automatic monthly budget reset"),
    budget_service: BudgetService = Depends(get_budget_service),
):
    """Toggle automatic monthly budget reset."""
    try:
        budget_service.toggle_auto_reset(enabled)

        return {
            "message": f"Auto-reset {'enabled' if enabled else 'disabled'} successfully",
            "auto_reset": enabled,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error toggling auto-reset: {str(e)}")


@router.get("/history", response_model=Dict[str, Any])
async def get_budget_history(
    budget_service: BudgetService = Depends(get_budget_service),
):
    """Get budget history for all months."""
    try:
        history = budget_service.get_budget_history()
        budget = budget_service.budget_repo.load()

        history_dicts = []
        for monthly_budget in history:
            history_dicts.append({
                "month": monthly_budget.month,
                "budget_amount": monthly_budget.amount,
                "spent": monthly_budget.spent,
                "remaining": monthly_budget.remaining,
                "percentage": monthly_budget.percentage_used,
                "over_budget": monthly_budget.is_over_budget,
                "created_at": monthly_budget.created_at,
                "reset_from_previous": monthly_budget.reset_from_previous,
            })

        return {
            "history": history_dicts,
            "auto_reset": budget.auto_reset,
            "current_month": budget_service.get_current_month(),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting budget history: {str(e)}")


@router.delete("", response_model=Dict[str, str])
async def delete_current_budget(
    budget_service: BudgetService = Depends(get_budget_service),
):
    """Delete current month's budget."""
    try:
        budget_service.delete_current_budget()
        return {"message": "Current month's budget deleted successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting budget: {str(e)}")

