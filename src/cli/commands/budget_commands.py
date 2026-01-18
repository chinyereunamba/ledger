"""CLI commands for budget management."""

import typer
from typing import Optional
from rich import print as rprint

from ...ledger.services.budget_service import BudgetService
from ..presenters import TableFormatter


def register_budget_commands(app: typer.Typer, budget_service: BudgetService):
    """Register budget-related CLI commands."""

    formatter = TableFormatter()

    budget = typer.Typer()
    app.add_typer(budget, name="budget")

    @budget.command("set")
    def set_budget(amount: float = typer.Argument(..., help="Monthly budget amount")):
        """Set monthly budget amount"""
        try:
            monthly_budget = budget_service.set_monthly_budget(amount)
            rprint(f"[green]Budget set for {monthly_budget.month}: ₦{amount:,.2f}[/green]")
            rprint(f"Current spending: ₦{monthly_budget.spent:,.2f}")
            rprint(f"Remaining: ₦{monthly_budget.remaining:,.2f}")
        except ValueError as e:
            rprint(f"[red]{e}[/red]")
        except Exception as e:
            rprint(f"[red]Error setting budget: {e}[/red]")

    @budget.command("status")
    def budget_status():
        """Show current month's budget status"""
        try:
            monthly_budget = budget_service.get_budget_status()
            budget = budget_service.budget_repo.load()

            if monthly_budget.amount == 0:
                rprint(f"\n[yellow]No budget set for {monthly_budget.month}[/yellow]")
                rprint("Use 'ledger budget set <amount>' to set a monthly budget")
                return

            budget_data = {
                "budget_amount": monthly_budget.amount,
                "spent": monthly_budget.spent,
                "remaining": monthly_budget.remaining,
                "percentage": monthly_budget.percentage_used,
                "over_budget": monthly_budget.is_over_budget,
            }

            rprint(f"\n[bold blue]Budget Status for {monthly_budget.month}[/bold blue]")
            table = formatter.format_budget_table(budget_data)
            formatter.print_table(table)

            # Show status message
            percentage = monthly_budget.percentage_used
            if percentage > 90:
                rprint("[red]⚠️  Warning: You've used over 90% of your budget![/red]")
            elif percentage > 75:
                rprint("[yellow]⚠️  Caution: You've used over 75% of your budget[/yellow]")
            elif percentage > 50:
                rprint("[blue]ℹ️  You've used over half of your budget[/blue]")
            else:
                rprint("[green]✅ You're on track with your budget[/green]")

        except Exception as e:
            rprint(f"[red]Error getting budget status: {e}[/red]")

    @budget.command("history")
    def budget_history():
        """Show budget history for all months"""
        try:
            history = budget_service.get_budget_history()
            budget = budget_service.budget_repo.load()

            if not history:
                rprint("[yellow]No budget history found[/yellow]")
                return

            rprint("\n[bold blue]Budget History[/bold blue]")

            history_dicts = []
            for monthly_budget in history:
                history_dicts.append({
                    "month": monthly_budget.month,
                    "budget_amount": monthly_budget.amount,
                    "spent": monthly_budget.spent,
                    "remaining": monthly_budget.remaining,
                    "over_budget": monthly_budget.is_over_budget,
                })

            table = formatter.format_budget_history_table(history_dicts)
            formatter.print_table(table)

            auto_reset_status = "Enabled" if budget.auto_reset else "Disabled"
            rprint(f"\n[dim]Auto-reset: {auto_reset_status}[/dim]")

        except Exception as e:
            rprint(f"[red]Error getting budget history: {e}[/red]")

    @budget.command("auto-reset")
    def budget_auto_reset(
        enable: Optional[bool] = typer.Option(None, "--enable/--disable", help="Enable or disable auto-reset")
    ):
        """Toggle automatic monthly budget reset"""
        try:
            enabled = budget_service.toggle_auto_reset(enable)
            status = "enabled" if enabled else "disabled"
            rprint(f"[green]Auto-reset {status} successfully[/green]")

            if enabled:
                rprint("[dim]Your budget will automatically reset each month with the same amount[/dim]")
            else:
                rprint("[dim]You'll need to manually set your budget each month[/dim]")

        except Exception as e:
            rprint(f"[red]Error toggling auto-reset: {e}[/red]")

