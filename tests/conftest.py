"""Pytest configuration and fixtures."""

import pytest
import tempfile
import shutil
from pathlib import Path

from src.ledger.config import reset_settings, reset_paths
from src.ledger.repositories import (
    ExpenseRepository,
    CategoryRepository,
    BudgetRepository,
    UserRepository,
    FileManager,
)
from src.ledger.services import (
    ExpenseService,
    CategoryService,
    BudgetService,
    AnalyticsService,
    UserService,
)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test data."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def test_settings(temp_dir):
    """Create test settings with temporary directory."""
    reset_settings(temp_dir)
    reset_paths(temp_dir)
    from src.ledger.config import get_settings

    yield get_settings()
    reset_settings()
    reset_paths()


@pytest.fixture
def file_manager(test_settings):
    """Create a file manager instance."""
    return FileManager(test_settings)


@pytest.fixture
def expense_repository(file_manager):
    """Create an expense repository instance."""
    return ExpenseRepository()


@pytest.fixture
def category_repository(file_manager):
    """Create a category repository instance."""
    return CategoryRepository()


@pytest.fixture
def budget_repository(file_manager):
    """Create a budget repository instance."""
    return BudgetRepository()


@pytest.fixture
def user_repository(file_manager):
    """Create a user repository instance."""
    return UserRepository()


@pytest.fixture
def expense_service(expense_repository):
    """Create an expense service instance."""
    return ExpenseService(expense_repository)


@pytest.fixture
def category_service(category_repository):
    """Create a category service instance."""
    return CategoryService(category_repository)


@pytest.fixture
def budget_service(budget_repository, expense_repository):
    """Create a budget service instance."""
    return BudgetService(budget_repository, expense_repository)


@pytest.fixture
def analytics_service(expense_repository, category_service):
    """Create an analytics service instance."""
    return AnalyticsService(expense_repository, category_service)


@pytest.fixture
def user_service(user_repository):
    """Create a user service instance."""
    return UserService(user_repository)


@pytest.fixture
def sample_expenses():
    """Sample expense data for testing."""
    return {
        "2025-01-15": [
            {"expense": "Lunch", "amount": 1500},
            {"expense": "Transport", "amount": 500},
        ],
        "2025-01-16": [
            {"expense": "Coffee", "amount": 300},
        ],
    }

