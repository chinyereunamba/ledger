"""Budget domain models."""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional


@dataclass
class MonthlyBudget:
    """
    Represents a monthly budget.

    Attributes:
        month: Month in YYYY-MM format
        amount: Budget amount
        spent: Amount spent (calculated)
        created_at: Creation timestamp
        reset_from_previous: Whether this was auto-reset from previous month
    """

    month: str
    amount: float
    spent: float = 0.0
    created_at: Optional[str] = None
    reset_from_previous: bool = False

    def __post_init__(self) -> None:
        """Validate and set defaults."""
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if self.amount < 0:
            raise ValueError("Budget amount cannot be negative")

    @property
    def remaining(self) -> float:
        """Calculate remaining budget."""
        return self.amount - self.spent

    @property
    def percentage_used(self) -> float:
        """Calculate percentage of budget used."""
        if self.amount == 0:
            return 0.0
        return min((self.spent / self.amount) * 100, 100.0)

    @property
    def is_over_budget(self) -> bool:
        """Check if over budget."""
        return self.spent > self.amount

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "amount": self.amount,
            "spent": self.spent,
            "created_at": self.created_at,
            "reset_from_previous": self.reset_from_previous,
        }

    @classmethod
    def from_dict(cls, month: str, data: dict) -> "MonthlyBudget":
        """Create from dictionary."""
        return cls(
            month=month,
            amount=data.get("amount", 0),
            spent=data.get("spent", 0),
            created_at=data.get("created_at"),
            reset_from_previous=data.get("reset_from_previous", False),
        )


@dataclass
class Budget:
    """
    Represents budget configuration and history.

    Attributes:
        monthly_budgets: Dictionary mapping month (YYYY-MM) to MonthlyBudget
        current_month: Current month in YYYY-MM format
        auto_reset: Whether to auto-reset budget each month
    """

    monthly_budgets: Dict[str, MonthlyBudget]
    current_month: str
    auto_reset: bool = True

    def __post_init__(self) -> None:
        """Set current month if not provided."""
        if not self.current_month:
            self.current_month = datetime.now().strftime("%Y-%m")

    def get_current_budget(self) -> Optional[MonthlyBudget]:
        """Get current month's budget."""
        return self.monthly_budgets.get(self.current_month)

    def set_monthly_budget(self, month: str, amount: float) -> MonthlyBudget:
        """
        Set budget for a specific month.

        Args:
            month: Month in YYYY-MM format
            amount: Budget amount

        Returns:
            Created MonthlyBudget instance
        """
        budget = MonthlyBudget(month=month, amount=amount)
        self.monthly_budgets[month] = budget
        return budget

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "monthly_budgets": {
                month: budget.to_dict()
                for month, budget in self.monthly_budgets.items()
            },
            "current_month": self.current_month,
            "auto_reset": self.auto_reset,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Budget":
        """Create from dictionary."""
        monthly_budgets = {
            month: MonthlyBudget.from_dict(month, budget_data)
            for month, budget_data in data.get("monthly_budgets", {}).items()
        }
        return cls(
            monthly_budgets=monthly_budgets,
            current_month=data.get("current_month", datetime.now().strftime("%Y-%m")),
            auto_reset=data.get("auto_reset", True),
        )

    @classmethod
    def create_default(cls) -> "Budget":
        """Create default budget instance."""
        return cls(
            monthly_budgets={},
            current_month=datetime.now().strftime("%Y-%m"),
            auto_reset=True,
        )

