"""Service for category business logic."""

from typing import Dict, List, Optional

from ..domain.category import Category
from ..repositories import CategoryRepository


class CategoryService:
    """Service for category operations."""

    def __init__(self, repository: Optional[CategoryRepository] = None):
        """
        Initialize category service.

        Args:
            repository: CategoryRepository instance. Creates new one if None.
        """
        self.repository = repository or CategoryRepository()

    def get_all_categories(self) -> Dict[str, Category]:
        """
        Get all categories.

        Returns:
            Dictionary mapping category names to Category instances
        """
        return self.repository.load_all()

    def get_category(self, name: str) -> Optional[Category]:
        """
        Get a category by name.

        Args:
            name: Category name

        Returns:
            Category instance or None if not found
        """
        return self.repository.get_category(name)

    def add_category(self, name: str, keywords: Optional[List[str]] = None) -> Category:
        """
        Add a new category.

        Args:
            name: Category name
            keywords: List of keywords for the category

        Returns:
            Created Category instance
        """
        if keywords is None:
            keywords = []
        category = Category(name=name, keywords=keywords)
        self.repository.add_category(category)
        return category

    def remove_category(self, name: str) -> None:
        """
        Remove a category.

        Args:
            name: Category name to remove
        """
        self.repository.remove_category(name)

    def update_category(self, name: str, keywords: List[str]) -> Category:
        """
        Update a category's keywords.

        Args:
            name: Category name
            keywords: New list of keywords

        Returns:
            Updated Category instance
        """
        category = Category(name=name, keywords=keywords)
        self.repository.update_category(category)
        return category

    def categorize_expense(self, expense_name: str) -> str:
        """
        Determine category for an expense.

        Args:
            expense_name: Name of the expense

        Returns:
            Category name (defaults to "miscellaneous")
        """
        categories = self.get_all_categories()
        expense_lower = expense_name.lower().strip()

        # Check each category for matches
        for category in categories.values():
            if category.matches(expense_name):
                return category.name

        return "miscellaneous"

    def get_category_summary(
        self, expenses_data: Dict[str, List[Dict]]
    ) -> Dict[str, float]:
        """
        Calculate spending by category.

        Args:
            expenses_data: Dictionary mapping dates to expense lists

        Returns:
            Dictionary mapping category names to total amounts
        """
        category_totals: Dict[str, float] = {}

        for expenses in expenses_data.values():
            for expense in expenses:
                category = self.categorize_expense(expense["expense"])
                amount = float(expense["amount"])
                category_totals[category] = category_totals.get(category, 0) + amount

        return category_totals

