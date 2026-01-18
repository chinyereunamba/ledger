"""Repository for category data access."""

from typing import Dict, List, Optional

from ..config import get_settings
from ..domain.category import Category
from .file_manager import FileManager


class CategoryRepository:
    """Repository for category CRUD operations."""

    def __init__(self, file_manager: Optional[FileManager] = None):
        """
        Initialize category repository.

        Args:
            file_manager: FileManager instance. Creates new one if None.
        """
        self.settings = get_settings()
        self.file_manager = file_manager or FileManager(self.settings)

    def load_all(self) -> Dict[str, Category]:
        """
        Load all categories from file.

        Returns:
            Dictionary mapping category names to Category instances
        """
        data = self.file_manager.load_json(
            self.settings.categories_file, default={}
        )
        if not data:
            # Return default categories if file is empty
            return Category.get_default_categories()
        return Category.from_dict(data)

    def save_all(self, categories: Dict[str, Category]) -> None:
        """
        Save all categories to file.

        Args:
            categories: Dictionary mapping category names to Category instances
        """
        data = {name: cat.keywords for name, cat in categories.items()}
        self.file_manager.save_json(self.settings.categories_file, data)

    def get_category(self, name: str) -> Optional[Category]:
        """
        Get a category by name.

        Args:
            name: Category name

        Returns:
            Category instance or None if not found
        """
        categories = self.load_all()
        return categories.get(name.lower())

    def add_category(self, category: Category) -> None:
        """
        Add a new category.

        Args:
            category: Category to add
        """
        categories = self.load_all()
        if category.name in categories:
            raise ValueError(f"Category '{category.name}' already exists")
        categories[category.name] = category
        self.save_all(categories)

    def remove_category(self, name: str) -> None:
        """
        Remove a category.

        Args:
            name: Category name to remove
        """
        categories = self.load_all()
        name_lower = name.lower()
        if name_lower not in categories:
            raise ValueError(f"Category '{name}' not found")
        del categories[name_lower]
        self.save_all(categories)

    def update_category(self, category: Category) -> None:
        """
        Update an existing category.

        Args:
            category: Category with updated data
        """
        categories = self.load_all()
        if category.name not in categories:
            raise ValueError(f"Category '{category.name}' not found")
        categories[category.name] = category
        self.save_all(categories)

