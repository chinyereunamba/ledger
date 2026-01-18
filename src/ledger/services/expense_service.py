"""Service for expense business logic."""

from typing import Dict, List, Optional
from datetime import datetime, timedelta

from ..domain.expense import Expense
from ..repositories import ExpenseRepository


class ExpenseService:
    """Service for expense operations."""

    def __init__(self, repository: Optional[ExpenseRepository] = None):
        """
        Initialize expense service.

        Args:
            repository: ExpenseRepository instance. Creates new one if None.
        """
        self.repository = repository or ExpenseRepository()

    def add_expense(
        self, expense_name: str, amount: float, date: Optional[str] = None
    ) -> Expense:
        """
        Add a new expense.

        Args:
            expense_name: Name/description of the expense
            amount: Amount spent
            date: Optional date (YYYY-MM-DD). Defaults to today.

        Returns:
            Created Expense instance
        """
        expense = Expense.create(expense_name, amount, date)
        self.repository.add_expense(expense)
        return expense

    def get_expenses_by_date(self, date: str) -> List[Dict]:
        """
        Get expenses for a specific date.

        Args:
            date: Date in YYYY-MM-DD format

        Returns:
            List of expense dictionaries
        """
        return self.repository.get_expenses_by_date(date)

    def get_expenses_by_week(self) -> Dict[str, List[Dict]]:
        """
        Get expenses for the current week (last 7 days).

        Returns:
            Dictionary mapping dates to expense lists
        """
        return self.repository.get_expenses_by_week()

    def get_expenses_by_range(
        self, start_date: str, end_date: str
    ) -> Dict[str, List[Dict]]:
        """
        Get expenses within a date range.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            Dictionary mapping dates to expense lists
        """
        if start_date > end_date:
            raise ValueError("Start date cannot be after end date")
        return self.repository.get_expenses_by_range(start_date, end_date)

    def update_expense(
        self,
        date: str,
        identifier: str | int,
        expense: Optional[str] = None,
        amount: Optional[float] = None,
    ) -> None:
        """
        Update an expense.

        Args:
            date: Date of the expense
            identifier: Index (int) or expense name (str)
            expense: New expense name (optional)
            amount: New amount (optional)
        """
        if not expense and not amount:
            raise ValueError("At least one of expense or amount must be provided")

        # Find index
        if isinstance(identifier, int):
            index = identifier
        else:
            index = self.repository.find_expense_by_name(date, identifier)
            if index is None:
                raise ValueError(
                    f"Expense '{identifier}' not found on date {date}"
                )

        self.repository.update_expense(date, index, expense, amount)

    def delete_expense(self, date: str, identifier: str | int) -> None:
        """
        Delete an expense.

        Args:
            date: Date of the expense
            identifier: Index (int) or expense name (str)
        """
        # Find index
        if isinstance(identifier, int):
            index = identifier
        else:
            index = self.repository.find_expense_by_name(date, identifier)
            if index is None:
                raise ValueError(
                    f"Expense '{identifier}' not found on date {date}"
                )

        self.repository.delete_expense(date, index)

    def delete_all(self) -> None:
        """Delete all expenses."""
        self.repository.delete_all()

    def get_all_expenses(self) -> Dict[str, List[Dict]]:
        """
        Get all expenses.

        Returns:
            Dictionary mapping dates to expense lists
        """
        return self.repository.load_all()

    def calculate_daily_total(self, date: str) -> float:
        """
        Calculate total expenses for a date.

        Args:
            date: Date in YYYY-MM-DD format

        Returns:
            Total amount
        """
        expenses = self.get_expenses_by_date(date)
        return sum(float(exp["amount"]) for exp in expenses)

    def calculate_range_total(
        self, start_date: str, end_date: str
    ) -> float:
        """
        Calculate total expenses for a date range.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            Total amount
        """
        expenses_dict = self.get_expenses_by_range(start_date, end_date)
        total = 0.0
        for expenses in expenses_dict.values():
            total += sum(float(exp["amount"]) for exp in expenses)
        return total

