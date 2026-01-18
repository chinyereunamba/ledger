"""Expense domain model."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class Expense:
    """
    Represents a single expense entry.

    Attributes:
        expense: Name/description of the expense
        amount: Amount spent
        date: Date of the expense (YYYY-MM-DD format)
    """

    expense: str
    amount: float
    date: str

    def __post_init__(self) -> None:
        """Validate expense data."""
        if not self.expense or not self.expense.strip():
            raise ValueError("Expense name cannot be empty")
        if self.amount < 0:
            raise ValueError("Expense amount cannot be negative")
        if not self._is_valid_date(self.date):
            raise ValueError(f"Invalid date format: {self.date}. Use YYYY-MM-DD")

    @staticmethod
    def _is_valid_date(date_str: str) -> bool:
        """Validate date string format."""
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    @classmethod
    def create(
        cls, expense: str, amount: float, date: Optional[str] = None
    ) -> "Expense":
        """
        Create an expense with optional date (defaults to today).

        Args:
            expense: Name/description of the expense
            amount: Amount spent
            date: Optional date (YYYY-MM-DD). Defaults to today.

        Returns:
            Expense instance
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        return cls(expense=expense.strip().title(), amount=amount, date=date)

    def to_dict(self) -> dict:
        """Convert expense to dictionary."""
        return {"expense": self.expense, "amount": self.amount}

