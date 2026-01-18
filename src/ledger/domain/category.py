"""Category domain model."""

from dataclasses import dataclass
from typing import List, Dict


@dataclass
class Category:
    """
    Represents an expense category.

    Attributes:
        name: Category name (lowercase)
        keywords: List of keywords that match this category
    """

    name: str
    keywords: List[str]

    def __post_init__(self) -> None:
        """Normalize category name."""
        self.name = self.name.lower().strip()
        if not self.name:
            raise ValueError("Category name cannot be empty")

    def matches(self, expense_name: str) -> bool:
        """
        Check if an expense name matches this category.

        Args:
            expense_name: Name of the expense to check

        Returns:
            True if the expense matches this category
        """
        expense_lower = expense_name.lower().strip()

        # Check for exact matches first
        if expense_lower in [kw.lower() for kw in self.keywords]:
            return True

        # Check for partial matches
        return any(kw.lower() in expense_lower for kw in self.keywords)

    def to_dict(self) -> Dict[str, List[str]]:
        """Convert category to dictionary."""
        return {self.name: self.keywords}

    @classmethod
    def from_dict(cls, data: Dict[str, List[str]]) -> Dict[str, "Category"]:
        """
        Create categories from dictionary.

        Args:
            data: Dictionary mapping category names to keyword lists

        Returns:
            Dictionary of Category instances
        """
        return {
            name.lower(): cls(name=name, keywords=keywords)
            for name, keywords in data.items()
        }

    @classmethod
    def get_default_categories(cls) -> Dict[str, "Category"]:
        """Get default categories."""
        default_data = {
            "food": [
                "food",
                "lunch",
                "dinner",
                "breakfast",
                "brunch",
                "snacks",
                "groceries",
                "restaurant",
                "bread",
                "rice",
                "moi-moi",
                "soup",
                "fish",
                "milk",
                "pear",
                "ice",
                "water",
                "drink",
                "juice",
                "tea",
                "coffee",
                "groundnut",
                "meal",
            ],
            "transport": [
                "transport",
                "fuel",
                "taxi",
                "bus",
                "train",
                "uber",
            ],
            "utilities": [
                "utilities",
                "electricity",
                "water",
                "internet",
                "phone",
                "gas",
            ],
            "entertainment": [
                "entertainment",
                "movie",
                "games",
                "music",
                "books",
                "streaming",
            ],
            "health": [
                "health",
                "medicine",
                "doctor",
                "hospital",
                "pharmacy",
                "fitness",
            ],
            "shopping": [
                "shopping",
                "clothes",
                "electronics",
                "household",
                "gifts",
            ],
            "education": [
                "education",
                "books",
                "courses",
                "tuition",
                "training",
                "textbook",
            ],
            "miscellaneous": [],
        }
        return cls.from_dict(default_data)

