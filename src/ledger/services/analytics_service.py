"""Service for analytics and statistics."""

from typing import Dict, List, Tuple, Optional
from datetime import datetime
import pandas as pd

from ..repositories import ExpenseRepository
from .category_service import CategoryService


class AnalyticsService:
    """Service for analytics and statistics calculations."""

    def __init__(
        self,
        expense_repository: Optional[ExpenseRepository] = None,
        category_service: Optional[CategoryService] = None,
    ):
        """
        Initialize analytics service.

        Args:
            expense_repository: ExpenseRepository instance
            category_service: CategoryService instance
        """
        self.expense_repo = expense_repository or ExpenseRepository()
        self.category_service = category_service or CategoryService()

    def calculate_summary_stats(
        self, expenses_data: Dict[str, List[Dict]], period_description: str
    ) -> Dict:
        """
        Calculate summary statistics for expenses.

        Args:
            expenses_data: Dictionary mapping dates to expense lists
            period_description: Description of the time period

        Returns:
            Dictionary with summary statistics
        """
        total = 0.0
        all_expenses = []
        transaction_count = 0
        days_with_expenses = len([d for d in expenses_data.keys() if expenses_data[d]])

        for date, expenses in expenses_data.items():
            for exp in expenses:
                exp_with_date = exp.copy()
                exp_with_date["date"] = date
                all_expenses.append(exp_with_date)
                total += float(exp["amount"])
                transaction_count += 1

        return {
            "total": round(total, 2),
            "expenses": all_expenses,
            "period": period_description,
            "transaction_count": transaction_count,
            "days_with_expenses": days_with_expenses,
        }

    def calculate_comprehensive_stats(self) -> Dict:
        """
        Calculate comprehensive statistics for all expenses.

        Returns:
            Dictionary with comprehensive statistics
        """
        data = self.expense_repo.load_all()

        if not data:
            return self._empty_stats()

        # Flatten data for analysis
        records = []
        category_totals: Dict[str, float] = {}
        daily_totals: Dict[str, float] = {}
        monthly_totals: Dict[str, float] = {}
        expense_counts: Dict[str, int] = {}

        for date, expenses in data.items():
            daily_total = 0.0
            month = date[:7]  # Extract YYYY-MM

            for item in expenses:
                amount = float(item["amount"])
                expense_name = item["expense"]

                records.append(
                    {
                        "date": date,
                        "expense": expense_name,
                        "amount": amount,
                    }
                )

                # Track totals
                daily_total += amount
                monthly_totals[month] = monthly_totals.get(month, 0) + amount

                # Track expense frequency
                expense_counts[expense_name] = expense_counts.get(expense_name, 0) + 1

                # Track category totals
                category = self.category_service.categorize_expense(expense_name)
                category_totals[category] = category_totals.get(category, 0) + amount

            daily_totals[date] = daily_total

        # Calculate derived stats
        df = pd.DataFrame(records)
        if len(df) == 0:
            return self._empty_stats()

        df["date"] = pd.to_datetime(df["date"])

        total_spent = df["amount"].sum()
        total_days = (df["date"].max() - df["date"].min()).days + 1
        avg_daily = total_spent / total_days if total_days > 0 else 0

        # Most expensive day
        most_expensive_day = max(daily_totals.items(), key=lambda x: x[1]) if daily_totals else (None, 0)

        # Top category
        top_category = max(category_totals.items(), key=lambda x: x[1]) if category_totals else (None, 0)

        # Most frequent expense
        most_frequent_expense = max(expense_counts.items(), key=lambda x: x[1]) if expense_counts else (None, 0)

        # Top expenses by total amount
        expense_totals = df.groupby("expense")["amount"].sum().sort_values(ascending=False)
        top_expenses = [
            {"name": name, "total_amount": round(amount, 2)}
            for name, amount in expense_totals.head(5).items()
        ]

        # Top categories
        top_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)[:5]
        top_categories_list = [
            {"name": name, "total_amount": round(amount, 2)}
            for name, amount in top_categories
        ]

        # Current month stats
        current_month = datetime.now().strftime("%Y-%m")
        current_month_spent = monthly_totals.get(current_month, 0)

        return {
            "total_spent": round(total_spent, 2),
            "daily_average": round(avg_daily, 2),
            "transaction_count": len(df),
            "days_tracked": total_days,
            "most_spent_category": {
                "name": top_category[0],
                "amount": round(top_category[1], 2),
            }
            if top_category[0]
            else None,
            "most_frequent_expense": {
                "name": most_frequent_expense[0],
                "count": most_frequent_expense[1],
            }
            if most_frequent_expense[0]
            else None,
            "most_expensive_day": {
                "date": most_expensive_day[0],
                "amount": round(most_expensive_day[1], 2),
            }
            if most_expensive_day[0]
            else None,
            "top_expenses": top_expenses,
            "top_categories": top_categories_list,
            "category_breakdown": {
                name: round(amount, 2) for name, amount in category_totals.items()
            },
            "monthly_spending": {
                month: round(amount, 2) for month, amount in monthly_totals.items()
            },
            "current_month_spent": round(current_month_spent, 2),
        }

    def _empty_stats(self) -> Dict:
        """Return empty statistics structure."""
        return {
            "total_spent": 0,
            "daily_average": 0,
            "transaction_count": 0,
            "days_tracked": 0,
            "most_spent_category": None,
            "most_frequent_expense": None,
            "most_expensive_day": None,
            "top_expenses": [],
            "top_categories": [],
            "category_breakdown": {},
            "monthly_spending": {},
            "current_month_spent": 0,
        }

    def get_monthly_stats(self, month: str) -> Dict:
        """
        Get statistics for a specific month.

        Args:
            month: Month in YYYY-MM format

        Returns:
            Dictionary with monthly statistics
        """
        data = self.expense_repo.load_all()
        month_data = {date: expenses for date, expenses in data.items() if date.startswith(month)}

        if not month_data:
            return {
                "month": month,
                "total_spent": 0,
                "transaction_count": 0,
                "days_tracked": 0,
                "daily_average": 0,
                "categories": {},
                "top_expenses": [],
            }

        total_spent = 0.0
        category_totals: Dict[str, float] = {}
        expense_totals: Dict[str, float] = {}
        transaction_count = 0

        for date, expenses in month_data.items():
            for expense in expenses:
                amount = float(expense["amount"])
                expense_name = expense["expense"]

                total_spent += amount
                transaction_count += 1

                # Track category totals
                category = self.category_service.categorize_expense(expense_name)
                category_totals[category] = category_totals.get(category, 0) + amount

                # Track expense totals
                expense_totals[expense_name] = expense_totals.get(expense_name, 0) + amount

        days_tracked = len(month_data)
        daily_average = total_spent / days_tracked if days_tracked > 0 else 0

        # Top expenses
        top_expenses = sorted(expense_totals.items(), key=lambda x: x[1], reverse=True)[:10]

        return {
            "month": month,
            "total_spent": round(total_spent, 2),
            "transaction_count": transaction_count,
            "days_tracked": days_tracked,
            "daily_average": round(daily_average, 2),
            "categories": {name: round(amount, 2) for name, amount in category_totals.items()},
            "top_expenses": [
                {"name": name, "amount": round(amount, 2)} for name, amount in top_expenses
            ],
        }

