"""Unit tests for ExpenseService."""

import pytest
from datetime import datetime

from src.ledger.services.expense_service import ExpenseService
from src.ledger.repositories.expense_repository import ExpenseRepository


@pytest.mark.unit
class TestExpenseService:
    """Test cases for ExpenseService."""

    def test_add_expense(self, expense_service):
        """Test adding an expense."""
        expense = expense_service.add_expense("Coffee", 500.0)
        assert expense.expense == "Coffee"
        assert expense.amount == 500.0
        assert expense.date == datetime.now().strftime("%Y-%m-%d")

    def test_add_expense_with_date(self, expense_service):
        """Test adding an expense with specific date."""
        expense = expense_service.add_expense("Lunch", 1500.0, "2025-01-15")
        assert expense.date == "2025-01-15"

    def test_get_expenses_by_date(self, expense_service, sample_expenses):
        """Test getting expenses by date."""
        # Add sample expenses
        for date, expenses in sample_expenses.items():
            for exp in expenses:
                expense_service.add_expense(exp["expense"], exp["amount"], date)

        expenses = expense_service.get_expenses_by_date("2025-01-15")
        assert len(expenses) == 2
        assert expenses[0]["expense"] == "Lunch"

    def test_calculate_daily_total(self, expense_service):
        """Test calculating daily total."""
        expense_service.add_expense("Item1", 100.0, "2025-01-15")
        expense_service.add_expense("Item2", 200.0, "2025-01-15")

        total = expense_service.calculate_daily_total("2025-01-15")
        assert total == 300.0

    def test_update_expense(self, expense_service):
        """Test updating an expense."""
        expense_service.add_expense("Coffee", 500.0, "2025-01-15")
        expense_service.update_expense("2025-01-15", 0, expense="Tea", amount=600.0)

        expenses = expense_service.get_expenses_by_date("2025-01-15")
        assert expenses[0]["expense"] == "Tea"
        assert expenses[0]["amount"] == 600.0

    def test_delete_expense(self, expense_service):
        """Test deleting an expense."""
        expense_service.add_expense("Coffee", 500.0, "2025-01-15")
        expense_service.delete_expense("2025-01-15", 0)

        expenses = expense_service.get_expenses_by_date("2025-01-15")
        assert len(expenses) == 0

    def test_get_expenses_by_range(self, expense_service, sample_expenses):
        """Test getting expenses by date range."""
        # Add sample expenses
        for date, expenses in sample_expenses.items():
            for exp in expenses:
                expense_service.add_expense(exp["expense"], exp["amount"], date)

        expenses_dict = expense_service.get_expenses_by_range("2025-01-15", "2025-01-16")
        assert "2025-01-15" in expenses_dict
        assert "2025-01-16" in expenses_dict

    def test_invalid_date_range(self, expense_service):
        """Test that invalid date range raises error."""
        with pytest.raises(ValueError, match="Start date cannot be after end date"):
            expense_service.get_expenses_by_range("2025-01-16", "2025-01-15")

