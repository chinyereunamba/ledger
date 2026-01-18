"""Rich table formatting for CLI output."""

from typing import Dict, List, Optional
from rich.table import Table
from rich.console import Console
from rich import print as rprint


class TableFormatter:
    """Formats data as Rich tables for CLI display."""

    def __init__(self):
        """Initialize table formatter."""
        self.console = Console()

    def format_expenses_table(
        self, expenses: List[Dict], date: str, title: Optional[str] = None
    ) -> Table:
        """
        Format expenses as a table.

        Args:
            expenses: List of expense dictionaries
            date: Date string
            title: Optional table title

        Returns:
            Rich Table instance
        """
        if title is None:
            from datetime import datetime

            today = datetime.today().strftime("%Y-%m-%d")
            if date == today:
                title = f"\nToday's summary: {date}"
            else:
                title = f"\nSummary for {date}"

        table = Table("Expense", "Amount")
        total = 0.0

        for expense in expenses:
            amount = float(expense["amount"])
            total += amount
            table.add_row(str(expense["expense"]).title(), f"₦{amount:,.2f}")

        table.add_row("[bold green]Total[/bold green]", f"[bold green]₦{total:,.2f}[/bold green]")

        return table

    def format_range_table(
        self,
        expenses_data: Dict[str, List[Dict]],
        start_date: str,
        end_date: str,
        total: float,
        stats: Optional[Dict] = None,
    ) -> tuple[Table, Table]:
        """
        Format date range expenses as tables.

        Args:
            expenses_data: Dictionary mapping dates to expense lists
            start_date: Start date
            end_date: End date
            total: Total amount
            stats: Optional statistics dictionary

        Returns:
            Tuple of (stats_table, expenses_table)
        """
        # Stats table
        stats_table = Table("Metric", "Value", title="📊 Range Summary")

        if stats:
            stats_table.add_row("Total Spent", f"₦{stats.get('total', total):,.2f}")
            stats_table.add_row(
                "Days with Expenses", str(stats.get("days_with_expenses", len(expenses_data)))
            )
            stats_table.add_row(
                "Total Transactions",
                str(stats.get("transaction_count", sum(len(e) for e in expenses_data.values()))),
            )
            if stats.get("days_with_expenses", 0) > 0:
                avg_daily = stats.get("total", total) / stats.get("days_with_expenses", 1)
                stats_table.add_row("Average per Day", f"₦{avg_daily:,.2f}")

        # Expenses table
        expenses_table = Table("Date", "Expense", "Amount", "Category")
        for date in sorted(expenses_data.keys()):
            for expense in expenses_data[date]:
                category = expense.get("category", "miscellaneous")
                expenses_table.add_row(
                    date,
                    expense["expense"],
                    f"₦{expense['amount']:,.2f}",
                    category.title(),
                )

        expenses_table.add_row(
            "",
            "[bold green]Total for Range[/bold green]",
            f"[bold green]₦{total:,.2f}[/bold green]",
            "",
        )

        return stats_table, expenses_table

    def format_summary_table(
        self, expenses_data: Dict[str, List[Dict]], total: float, period: str = "All time"
    ) -> Table:
        """
        Format summary table.

        Args:
            expenses_data: Dictionary mapping dates to expense lists
            total: Total amount
            period: Period description

        Returns:
            Rich Table instance
        """
        table = Table("Date", "Expense", "Amount", title=f"Summary: {period}")

        for date, expenses in sorted(expenses_data.items()):
            for expense in expenses:
                table.add_row(date, expense["expense"], f"₦{expense['amount']:,.2f}")

        table.add_row(
            "",
            "[bold green]Total Expenditure[/bold green]",
            f"[bold green]₦{total:,.2f}[/bold green]",
        )

        return table

    def format_category_table(self, category_totals: Dict[str, float]) -> Table:
        """
        Format category summary table.

        Args:
            category_totals: Dictionary mapping category names to amounts

        Returns:
            Rich Table instance
        """
        table = Table("Category", "Amount", "Percentage")
        total_spent = sum(category_totals.values())

        # Sort by amount
        sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)

        for category, amount in sorted_categories:
            percentage = (amount / total_spent * 100) if total_spent > 0 else 0
            table.add_row(category.title(), f"₦{amount:,.2f}", f"{percentage:.1f}%")

        table.add_row(
            "[bold]Total[/bold]",
            f"[bold]₦{total_spent:,.2f}[/bold]",
            "[bold]100.0%[/bold]",
        )

        return table

    def format_categories_list_table(self, categories: Dict[str, List[str]]) -> Table:
        """
        Format categories list table.

        Args:
            categories: Dictionary mapping category names to keyword lists

        Returns:
            Rich Table instance
        """
        table = Table("Category", "Keywords")
        for name, keywords in categories.items():
            keywords_str = ", ".join(keywords) if keywords else "[dim]No keywords[/dim]"
            table.add_row(name.title(), keywords_str)

        return table

    def format_stats_table(self, stats: Dict) -> tuple[Table, Table, Table, Table]:
        """
        Format comprehensive statistics tables.

        Args:
            stats: Statistics dictionary

        Returns:
            Tuple of (highlights_table, overview_table, categories_table, expenses_table)
        """
        # Highlights table
        highlights_table = Table("Key Metric", "Value", title="📈 Key Highlights")
        highlights_table.add_row(
            "💰 Average Daily Spending", f"₦{stats.get('daily_average', 0):,.2f}"
        )

        top_category = stats.get("most_spent_category")
        if top_category:
            highlights_table.add_row(
                "🏆 Top Category",
                f"{top_category['name'].title()} (₦{top_category['amount']:,.2f})",
            )

        most_expensive_day = stats.get("most_expensive_day")
        if most_expensive_day:
            highlights_table.add_row(
                "📅 Most Expensive Day",
                f"{most_expensive_day['date']} (₦{most_expensive_day['amount']:,.2f})",
            )

        # Overview table
        overview_table = Table("Metric", "Value", title="📋 Overview")
        overview_table.add_row("Total Spent", f"₦{stats.get('total_spent', 0):,.2f}")
        overview_table.add_row("Total Days Tracked", str(stats.get("days_tracked", 0)))
        overview_table.add_row("Total Transactions", str(stats.get("transaction_count", 0)))

        # Categories table
        categories_table = Table("Category", "Total Amount", "Percentage", title="🏷️ Top 5 Categories")
        top_categories = stats.get("top_categories", [])[:5]
        total_spent = stats.get("total_spent", 0)

        for cat in top_categories:
            percentage = (cat["total_amount"] / total_spent * 100) if total_spent > 0 else 0
            categories_table.add_row(
                cat["name"].title(),
                f"₦{cat['total_amount']:,.2f}",
                f"{percentage:.1f}%",
            )

        # Expenses table
        expenses_table = Table("Expense", "Total Amount", title="💸 Top 5 Individual Expenses")
        top_expenses = stats.get("top_expenses", [])[:5]

        for exp in top_expenses:
            expenses_table.add_row(exp["name"].title(), f"₦{exp['total_amount']:,.2f}")

        return highlights_table, overview_table, categories_table, expenses_table

    def format_budget_table(self, budget_data: Dict) -> Table:
        """
        Format budget status table.

        Args:
            budget_data: Budget data dictionary

        Returns:
            Rich Table instance
        """
        table = Table("Metric", "Amount")
        table.add_row("Budget", f"₦{budget_data.get('budget_amount', 0):,.2f}")
        table.add_row("Spent", f"₦{budget_data.get('spent', 0):,.2f}")
        table.add_row("Remaining", f"₦{budget_data.get('remaining', 0):,.2f}")
        table.add_row("Percentage Used", f"{budget_data.get('percentage', 0):.1f}%")

        if budget_data.get("over_budget", False):
            table.add_row(
                "[red]Over Budget[/red]",
                f"[red]₦{abs(budget_data.get('remaining', 0)):,.2f}[/red]",
            )

        return table

    def format_budget_history_table(self, history: List[Dict]) -> Table:
        """
        Format budget history table.

        Args:
            history: List of budget history dictionaries

        Returns:
            Rich Table instance
        """
        table = Table("Month", "Budget", "Spent", "Remaining", "Status")

        for item in history:
            if item.get("over_budget", False):
                status = f"[red]Over by ₦{abs(item.get('remaining', 0)):,.2f}[/red]"
            else:
                status = f"[green]Under by ₦{item.get('remaining', 0):,.2f}[/green]"

            table.add_row(
                item["month"],
                f"₦{item.get('budget_amount', 0):,.2f}",
                f"₦{item.get('spent', 0):,.2f}",
                f"₦{item.get('remaining', 0):,.2f}",
                status,
            )

        return table

    def format_backups_table(self, backups: List[Dict]) -> Table:
        """
        Format backups list table.

        Args:
            backups: List of backup dictionaries

        Returns:
            Rich Table instance
        """
        table = Table("File", "Date Created", "Size")
        for backup in backups:
            table.add_row(
                backup["name"],
                backup["created"],
                backup["size"],
            )
        return table

    def print_table(self, table: Table) -> None:
        """Print a Rich table."""
        self.console.print(table)

    def print_message(self, message: str, style: Optional[str] = None) -> None:
        """
        Print a styled message.

        Args:
            message: Message to print
            style: Optional Rich style string
        """
        if style:
            rprint(f"[{style}]{message}[/{style}]")
        else:
            rprint(message)

