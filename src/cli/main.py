"""Main CLI entry point."""

import typer
from rich import print as rprint
import json

from ...ledger.services import (
    ExpenseService,
    CategoryService,
    BudgetService,
    AnalyticsService,
    UserService,
)
from ...ledger.config import get_settings
from .commands.expense_commands import register_expense_commands
from .commands.analytics_commands import register_analytics_commands
from .commands.budget_commands import register_budget_commands
from .commands.category_commands import register_category_commands
from .commands.utility_commands import register_utility_commands
from .commands.user_commands import register_user_commands


def create_app() -> typer.Typer:
    """Create and configure the Typer CLI app."""
    app = typer.Typer(rich_markup_mode="rich")

    # Initialize services
    expense_service = ExpenseService()
    category_service = CategoryService()
    budget_service = BudgetService()
    analytics_service = AnalyticsService()
    user_service = UserService()

    # Register command groups
    register_expense_commands(app, expense_service)
    register_analytics_commands(app, analytics_service, expense_service)
    register_budget_commands(app, budget_service)
    register_category_commands(app, category_service)
    register_utility_commands(app)
    register_user_commands(app, user_service)

    @app.callback(invoke_without_command=True)
    def main(ctx: typer.Context):
        """
        Welcome to Ledger!

        A comprehensive command-line tool to track and analyze your daily expenses.
        """
        if ctx.invoked_subcommand is None:
            rprint("[bold green]📒 Welcome to Ledger![/bold green]")
            rprint("Track your daily expenses easily right from your terminal.\n")

            rprint("🧾 [bold]Core Commands:[/bold]")
            rprint("  • [cyan]add[/cyan]        - Add a new expense")
            rprint("  • [cyan]say[/cyan]        - Add expenses using natural language")
            rprint("  • [cyan]view[/cyan]       - View expenses by date/range")
            rprint("  • [cyan]edit[/cyan]       - Edit existing expenses")
            rprint("  • [cyan]delete[/cyan]     - Delete specific expenses")
            rprint("  • [cyan]stats[/cyan]      - View comprehensive analytics")
            rprint("  • [cyan]summary[/cyan]    - Show expense summaries")
            rprint("  • [cyan]categories[/cyan] - Manage expense categories")
            rprint("  • [cyan]export[/cyan]     - Export data to CSV")
            rprint("  • [cyan]backups[/cyan]    - View backup files")
            rprint("  • [cyan]info[/cyan]       - Show ledger information")
            rprint("  • [cyan]budget[/cyan]     - Manage monthly budgets")
            rprint("  • [cyan]clear[/cyan]      - Clear all expenses")
            rprint("  • [cyan]user[/cyan]       - User management\n")

            rprint("💡 [bold]Quick Examples:[/bold]")
            rprint("  [dim]ledger add \"Coffee\" 5.50[/dim]")
            rprint("  [dim]ledger say \"Bought airtime for 500 and lunch for 1500\"[/dim]")
            rprint("  [dim]ledger view --start 2025-07-01 --end 2025-07-20[/dim]")
            rprint("  [dim]ledger stats[/dim]")
            rprint("  [dim]ledger categories summary[/dim]\n")

            rprint("👉 Type [yellow]ledger COMMAND --help[/yellow] for detailed usage.\n")

            # Show ledger status and quick stats if data exists
            settings = get_settings()
            if settings.ledger_file.exists():
                try:
                    with open(settings.ledger_file, "r") as f:
                        data = json.load(f)
                    if data:
                        total_expenses = sum(len(expenses) for expenses in data.values())
                        rprint(
                            f"📈 [bold green]Current Status:[/bold green] {len(data)} days tracked, {total_expenses} transactions"
                        )
                    else:
                        rprint("📝 [dim]No expenses recorded yet. Start with 'ledger add'![/dim]")
                except Exception:
                    rprint("📝 [dim]Ready to track your expenses![/dim]")
            else:
                rprint(
                    "📝 [dim]Welcome! Your ledger will be created at ~/.ledger/ when you add your first expense.[/dim]"
                )

    return app


# Create the app instance
app = create_app()


if __name__ == "__main__":
    app()

