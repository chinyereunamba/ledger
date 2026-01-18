"""Dependency injection for API routes."""

from functools import lru_cache

from ..ledger.repositories import (
    ExpenseRepository,
    CategoryRepository,
    BudgetRepository,
    UserRepository,
)
from ..ledger.services import (
    ExpenseService,
    CategoryService,
    BudgetService,
    AnalyticsService,
    UserService,
)


@lru_cache()
def get_expense_repository() -> ExpenseRepository:
    """Get expense repository instance."""
    return ExpenseRepository()


@lru_cache()
def get_category_repository() -> CategoryRepository:
    """Get category repository instance."""
    return CategoryRepository()


@lru_cache()
def get_budget_repository() -> BudgetRepository:
    """Get budget repository instance."""
    return BudgetRepository()


@lru_cache()
def get_user_repository() -> UserRepository:
    """Get user repository instance."""
    return UserRepository()


@lru_cache()
def get_expense_service() -> ExpenseService:
    """Get expense service instance."""
    return ExpenseService(get_expense_repository())


@lru_cache()
def get_category_service() -> CategoryService:
    """Get category service instance."""
    return CategoryService(get_category_repository())


@lru_cache()
def get_budget_service() -> BudgetService:
    """Get budget service instance."""
    return BudgetService(get_budget_repository(), get_expense_repository())


@lru_cache()
def get_analytics_service() -> AnalyticsService:
    """Get analytics service instance."""
    return AnalyticsService(get_expense_repository(), get_category_service())


@lru_cache()
def get_user_service() -> UserService:
    """Get user service instance."""
    return UserService(get_user_repository())

