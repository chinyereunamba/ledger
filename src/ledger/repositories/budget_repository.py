"""Repository for budget data access."""

from typing import Optional

from ..config import get_settings
from ..domain.budget import Budget, MonthlyBudget
from .file_manager import FileManager


class BudgetRepository:
    """Repository for budget CRUD operations."""

    def __init__(self, file_manager: Optional[FileManager] = None):
        """
        Initialize budget repository.

        Args:
            file_manager: FileManager instance. Creates new one if None.
        """
        self.settings = get_settings()
        self.file_manager = file_manager or FileManager(self.settings)

    def load(self) -> Budget:
        """
        Load budget data from file.

        Returns:
            Budget instance
        """
        data = self.file_manager.load_json(self.settings.budget_file, default={})
        if not data:
            return Budget.create_default()
        return Budget.from_dict(data)

    def save(self, budget: Budget) -> None:
        """
        Save budget data to file.

        Args:
            budget: Budget instance to save
        """
        self.file_manager.save_json(self.settings.budget_file, budget.to_dict())

    def get_monthly_budget(self, month: str) -> Optional[MonthlyBudget]:
        """
        Get budget for a specific month.

        Args:
            month: Month in YYYY-MM format

        Returns:
            MonthlyBudget instance or None if not found
        """
        budget = self.load()
        return budget.monthly_budgets.get(month)

    def set_monthly_budget(self, month: str, amount: float) -> MonthlyBudget:
        """
        Set budget for a specific month.

        Args:
            month: Month in YYYY-MM format
            amount: Budget amount

        Returns:
            Created MonthlyBudget instance
        """
        budget = self.load()
        monthly_budget = budget.set_monthly_budget(month, amount)
        self.save(budget)
        return monthly_budget

    def update_monthly_spending(self, month: str, spent: float) -> None:
        """
        Update spending amount for a month.

        Args:
            month: Month in YYYY-MM format
            spent: Amount spent
        """
        budget = self.load()
        if month in budget.monthly_budgets:
            budget.monthly_budgets[month].spent = spent
            self.save(budget)

