"""Service for budget business logic."""

from typing import Optional
from datetime import datetime

from ..domain.budget import Budget, MonthlyBudget
from ..repositories import BudgetRepository, ExpenseRepository


class BudgetService:
    """Service for budget operations."""

    def __init__(
        self,
        budget_repository: Optional[BudgetRepository] = None,
        expense_repository: Optional[ExpenseRepository] = None,
    ):
        """
        Initialize budget service.

        Args:
            budget_repository: BudgetRepository instance
            expense_repository: ExpenseRepository instance
        """
        self.budget_repo = budget_repository or BudgetRepository()
        self.expense_repo = expense_repository or ExpenseRepository()

    def get_current_month(self) -> str:
        """Get current month in YYYY-MM format."""
        return datetime.now().strftime("%Y-%m")

    def get_monthly_spending(self, month: Optional[str] = None) -> float:
        """
        Calculate total spending for a month.

        Args:
            month: Month in YYYY-MM format. Defaults to current month.

        Returns:
            Total spending amount
        """
        if month is None:
            month = self.get_current_month()

        expenses_dict = self.expense_repo.load_all()
        total = 0.0

        for date_str, expenses in expenses_dict.items():
            if date_str.startswith(month):
                for expense in expenses:
                    total += float(expense["amount"])

        return total

    def reset_monthly_budget_if_needed(self) -> Budget:
        """
        Check and reset budget for new month if auto-reset is enabled.

        Returns:
            Updated Budget instance
        """
        budget = self.budget_repo.load()
        current_month = self.get_current_month()

        if budget.auto_reset and budget.current_month != current_month:
            # New month detected
            if budget.current_month and budget.monthly_budgets:
                # Get the most recent budget amount
                recent_budget = list(budget.monthly_budgets.values())[-1]
                recent_amount = recent_budget.amount

                # Set budget for current month with same amount
                budget.set_monthly_budget(
                    current_month, recent_amount
                )
                budget.monthly_budgets[current_month].reset_from_previous = True

            budget.current_month = current_month
            self.budget_repo.save(budget)

        return budget

    def set_monthly_budget(self, amount: float, month: Optional[str] = None) -> MonthlyBudget:
        """
        Set budget for a month.

        Args:
            amount: Budget amount
            month: Month in YYYY-MM format. Defaults to current month.

        Returns:
            Created MonthlyBudget instance
        """
        if amount < 0:
            raise ValueError("Budget amount must be positive")

        budget = self.reset_monthly_budget_if_needed()
        if month is None:
            month = self.get_current_month()

        # Calculate current spending
        current_spending = self.get_monthly_spending(month)

        # Set budget
        monthly_budget = budget.set_monthly_budget(month, amount)
        monthly_budget.spent = current_spending
        budget.monthly_budgets[month] = monthly_budget
        self.budget_repo.save(budget)

        return monthly_budget

    def get_budget_status(self, month: Optional[str] = None) -> MonthlyBudget:
        """
        Get budget status for a month.

        Args:
            month: Month in YYYY-MM format. Defaults to current month.

        Returns:
            MonthlyBudget instance with updated spending
        """
        budget = self.reset_monthly_budget_if_needed()
        if month is None:
            month = self.get_current_month()

        # Get or create monthly budget
        monthly_budget = budget.monthly_budgets.get(month)
        if monthly_budget is None:
            monthly_budget = MonthlyBudget(month=month, amount=0)

        # Update spending
        monthly_budget.spent = self.get_monthly_spending(month)
        budget.monthly_budgets[month] = monthly_budget
        self.budget_repo.save(budget)

        return monthly_budget

    def get_budget_history(self) -> List[MonthlyBudget]:
        """
        Get budget history for all months.

        Returns:
            List of MonthlyBudget instances, sorted by month (newest first)
        """
        budget = self.budget_repo.load()
        history = []

        for month, monthly_budget in budget.monthly_budgets.items():
            # Update spending for each month
            monthly_budget.spent = self.get_monthly_spending(month)
            history.append(monthly_budget)

        # Sort by month (newest first)
        history.sort(key=lambda b: b.month, reverse=True)
        return history

    def toggle_auto_reset(self, enabled: Optional[bool] = None) -> bool:
        """
        Toggle automatic monthly budget reset.

        Args:
            enabled: True to enable, False to disable, None to toggle

        Returns:
            New auto_reset setting
        """
        budget = self.budget_repo.load()

        if enabled is None:
            enabled = not budget.auto_reset

        budget.auto_reset = enabled
        self.budget_repo.save(budget)
        return enabled

    def delete_current_budget(self, month: Optional[str] = None) -> None:
        """
        Delete budget for a month.

        Args:
            month: Month in YYYY-MM format. Defaults to current month.
        """
        if month is None:
            month = self.get_current_month()

        budget = self.budget_repo.load()
        if month in budget.monthly_budgets:
            del budget.monthly_budgets[month]
            self.budget_repo.save(budget)

