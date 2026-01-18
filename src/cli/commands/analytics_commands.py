"""CLI commands for analytics and statistics."""

import typer
from typing import Optional
from rich import print as rprint
import pandas as pd
from datetime import datetime

from ...ledger.services.analytics_service import AnalyticsService
from ...ledger.services.expense_service import ExpenseService
from ..presenters import TableFormatter


def register_analytics_commands(app: typer.Typer, analytics_service: AnalyticsService, expense_service: ExpenseService):
    """Register analytics-related CLI commands."""

    formatter = TableFormatter()

    @app.command()
    def summary(
        all: bool = False,
        start: Optional[str] = None,
        end: Optional[str] = None,
    ):
        """
        Display a summary of expenses.

        Args:
            all: Show all-time summary.
            start: Start date for range summary (YYYY-MM-DD).
            end: End date for range summary (YYYY-MM-DD).
        """
        try:
            if start or end:
                if not start or not end:
                    rprint("[red]Both start and end dates are required for range summary.[/red]")
                    return
                expenses_dict = expense_service.get_expenses_by_range(start, end)
                period = f"from {start} to {end}"
            else:
                expenses_dict = expense_service.get_all_expenses()
                period = "All time"

            total = sum(
                sum(float(e["amount"]) for e in expenses)
                for expenses in expenses_dict.values()
            )

            table = formatter.format_summary_table(expenses_dict, total, period)
            formatter.print_table(table)

        except ValueError as e:
            rprint(f"[red]{e}[/red]")
        except Exception as e:
            rprint(f"[red]Error getting summary: {e}[/red]")

    @app.command()
    def stats():
        """Display comprehensive statistics about expenses."""
        try:
            stats_data = analytics_service.calculate_comprehensive_stats()

            highlights_table, overview_table, categories_table, expenses_table = formatter.format_stats_table(stats_data)

            rprint("\n[bold blue]📊 Ledger Statistics[/bold blue]")
            rprint("=" * 50)

            formatter.print_table(highlights_table)
            formatter.print_table(overview_table)
            formatter.print_table(categories_table)
            formatter.print_table(expenses_table)

        except Exception as e:
            rprint(f"[red]Error getting stats: {e}[/red]")

    @app.command()
    def export(
        csv: bool = typer.Option(True, help="Export to CSV format"),
        output: Optional[str] = typer.Option(None, "--output", "-o", help="Output filename"),
    ):
        """
        Export the ledger data to a CSV file.

        Examples:
            ledger export
            ledger export --output my_expenses.csv
        """
        if not csv:
            rprint("[yellow]Only CSV export is currently supported.[/yellow]")
            return

        try:
            from ...ledger.services.category_service import CategoryService
            category_service = CategoryService()

            expenses_dict = expense_service.get_all_expenses()

            # Flatten the data with categories
            flattened_data = []
            for date, expenses in expenses_dict.items():
                for expense in expenses:
                    category = category_service.categorize_expense(expense["expense"])
                    flattened_data.append({
                        "Date": date,
                        "Expense": expense["expense"],
                        "Amount": expense["amount"],
                        "Category": category.title(),
                    })

            # Convert to DataFrame
            df = pd.DataFrame(flattened_data)

            # Generate filename if not provided
            if not output:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output = f"ledger_export_{timestamp}.csv"

            # Write to CSV
            df.to_csv(output, encoding="utf-8", index=False)

            # Show summary
            total_amount = df['Amount'].astype(float).sum()
            rprint(f"✅ Exported {len(df)} transactions to {output}")
            rprint(f"📊 Total amount: ₦{total_amount:,.2f}")

        except Exception as e:
            rprint(f"[red]Error exporting data: {e}[/red]")

