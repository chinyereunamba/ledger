"""Unit tests for CategoryService."""

import pytest

from src.ledger.services.category_service import CategoryService
from src.ledger.repositories.category_repository import CategoryRepository


@pytest.mark.unit
class TestCategoryService:
    """Test cases for CategoryService."""

    def test_categorize_expense(self, category_service):
        """Test categorizing an expense."""
        category = category_service.categorize_expense("lunch")
        assert category == "food"

    def test_categorize_unknown_expense(self, category_service):
        """Test categorizing an unknown expense defaults to miscellaneous."""
        category = category_service.categorize_expense("unknown_item")
        assert category == "miscellaneous"

    def test_add_category(self, category_service):
        """Test adding a category."""
        category = category_service.add_category("travel", ["flight", "hotel"])
        assert category.name == "travel"
        assert "flight" in category.keywords

    def test_get_category_summary(self, category_service):
        """Test getting category summary."""
        expenses_data = {
            "2025-01-15": [
                {"expense": "Lunch", "amount": 1500},
                {"expense": "Transport", "amount": 500},
            ],
        }

        summary = category_service.get_category_summary(expenses_data)
        assert "food" in summary
        assert "transport" in summary
        assert summary["food"] == 1500.0
        assert summary["transport"] == 500.0

