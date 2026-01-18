"""Repository for expense data access."""

from typing import Dict, List, Optional
from datetime import datetime, timedelta

from ..config import get_settings
from ..domain.expense import Expense
from .file_manager import FileManager


class ExpenseRepository:
    """Repository for expense CRUD operations."""

    def __init__(self, file_manager: Optional[FileManager] = None):
        """
        Initialize expense repository.

        Args:
            file_manager: FileManager instance. Creates new one if None.
        """
        self.settings = get_settings()
        self.file_manager = file_manager or FileManager(self.settings)

    def load_all(self) -> Dict[str, List[Dict]]:
        """
        Load all expenses from file.

        Returns:
            Dictionary mapping dates (YYYY-MM-DD) to lists of expense dicts
        """
        return self.file_manager.load_json(self.settings.ledger_file, default={})

    def save_all(self, data: Dict[str, List[Dict]]) -> None:
        """
        Save all expenses to file.

        Args:
            data: Dictionary mapping dates to expense lists
        """
        self.file_manager.save_json(self.settings.ledger_file, data)

    def add_expense(self, expense: Expense) -> None:
        """
        Add a new expense.

        Args:
            expense: Expense to add
        """
        data = self.load_all()
        date_key = expense.date

        if date_key not in data:
            data[date_key] = []

        data[date_key].append(expense.to_dict())
        self.save_all(data)

    def get_expenses_by_date(self, date: str) -> List[Dict]:
        """
        Get expenses for a specific date.

        Args:
            date: Date in YYYY-MM-DD format

        Returns:
            List of expense dictionaries
        """
        data = self.load_all()
        return data.get(date, [])

    def get_expenses_by_week(self) -> Dict[str, List[Dict]]:
        """
        Get expenses for the current week (last 7 days).

        Returns:
            Dictionary mapping dates to expense lists
        """
        data = self.load_all()
        today = datetime.today()
        week_dates = [
            (today + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(-6, 1)
        ]
        return {date: data.get(date, []) for date in week_dates if date in data}

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
        data = self.load_all()
        return {
            date: expenses
            for date, expenses in data.items()
            if start_date <= date <= end_date
        }

    def update_expense(
        self,
        date: str,
        index: int,
        expense: Optional[str] = None,
        amount: Optional[float] = None,
    ) -> None:
        """
        Update an expense by date and index.

        Args:
            date: Date of the expense
            index: Index of the expense in the date's list
            expense: New expense name (optional)
            amount: New amount (optional)
        """
        data = self.load_all()
        if date not in data or index >= len(data[date]) or index < 0:
            raise ValueError(f"Expense not found at date {date}, index {index}")

        if expense is not None:
            data[date][index]["expense"] = expense.strip().title()
        if amount is not None:
            data[date][index]["amount"] = amount

        self.save_all(data)

    def delete_expense(self, date: str, index: int) -> None:
        """
        Delete an expense by date and index.

        Args:
            date: Date of the expense
            index: Index of the expense in the date's list
        """
        data = self.load_all()
        if date not in data or index >= len(data[date]) or index < 0:
            raise ValueError(f"Expense not found at date {date}, index {index}")

        data[date].pop(index)

        # Remove date key if no expenses remain
        if not data[date]:
            del data[date]

        self.save_all(data)

    def delete_all(self) -> None:
        """Delete all expenses."""
        self.save_all({})

    def find_expense_by_name(
        self, date: str, expense_name: str
    ) -> Optional[int]:
        """
        Find expense index by name (case-insensitive).

        Args:
            date: Date of the expense
            expense_name: Name of the expense

        Returns:
            Index of the expense, or None if not found
        """
        expenses = self.get_expenses_by_date(date)
        expense_name_lower = expense_name.lower()
        for i, expense in enumerate(expenses):
            if expense["expense"].lower() == expense_name_lower:
                return i
        return None

