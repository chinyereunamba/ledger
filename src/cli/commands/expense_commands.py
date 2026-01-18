"""CLI commands for expense management."""

import typer
from typing import Optional
from rich import print as rprint

from ...ledger.services.expense_service import ExpenseService
from ...ledger.parsers.nlp_parser import parse_and_enhance
from ..presenters import TableFormatter


def register_expense_commands(app: typer.Typer, expense_service: ExpenseService):
    """Register expense-related CLI commands."""

    formatter = TableFormatter()

    @app.command()
    def add(
        expense: Optional[str] = typer.Argument(None),
        amount: Optional[float] = typer.Argument(None),
    ):
        """Add expenses to the ledger via CLI arguments or interactive prompts."""
        while True:
            if not expense:
                expense = typer.prompt("What did you buy today?")

            if not amount:
                amount = typer.prompt(f"How much did you spend on {expense.title()}")

            try:
                amount = float(amount)
            except ValueError:
                rprint("[red]Amount must be a number. Try again.[/red]")
                expense = None
                amount = None
                continue

            expense_service.add_expense(expense, amount)
            rprint("✅ Expense saved successfully.")

            expense = None
            amount = None

            done = typer.confirm("Would that be all?")
            if done:
                break

        rprint("[bold green]All expenses added![/bold green]")

    @app.command()
    def say(input_text: str = typer.Argument(..., help="Natural language expense input")):
        """
        Add expenses using natural language.

        Examples:
            ledger say "Bought airtime for 500 and lunch for 1500"
            ledger say "Paid transport 800, airtime 300"
        """
        try:
            parsed_expenses = parse_and_enhance(input_text)

            if not parsed_expenses:
                rprint("[yellow]Could not parse any expenses from the input. Please try a different format.[/yellow]")
                return

            rprint(f"[blue]Parsed {len(parsed_expenses)} expense(s) from:[/blue] \"{input_text}\"")
            rprint()

            for expense_data in parsed_expenses:
                expense_service.add_expense(expense_data["expense"], expense_data["amount"])
                rprint(f"✅ Added: {expense_data['expense']} - ₦{expense_data['amount']}")

            rprint(f"\n[bold green]Successfully added {len(parsed_expenses)} expense(s)![/bold green]")

        except Exception as e:
            rprint(f"[red]Error processing natural language input: {e}[/red]")

    @app.command()
    def view(
        date: Optional[str] = None,
        week: bool = False,
        start: Optional[str] = None,
        end: Optional[str] = None,
    ):
        """
        View expenses by date, week, or date range.

        Args:
            date: Specific date (YYYY-MM-DD). Defaults to today.
            week: Show expenses for the last 7 days.
            start: Start date for range view (YYYY-MM-DD).
            end: End date for range view (YYYY-MM-DD).
        """
        from datetime import datetime

        if start or end:
            if not start:
                rprint("[red]Start date is required when using date range.[/red]")
                return
            if not end:
                rprint("[red]End date is required when using date range.[/red]")
                return

            try:
                expenses_dict = expense_service.get_expenses_by_range(start, end)
                total = expense_service.calculate_range_total(start, end)

                rprint(f"\n[bold blue]📅 Expenses from {start} to {end}[/bold blue]")
                rprint("=" * 60)

                # Calculate stats
                days_with_expenses = len(expenses_dict)
                transaction_count = sum(len(exp) for exp in expenses_dict.values())
                avg_daily = total / days_with_expenses if days_with_expenses > 0 else 0

                stats = {
                    "total": total,
                    "days_with_expenses": days_with_expenses,
                    "transaction_count": transaction_count,
                    "avg_daily": avg_daily,
                }

                stats_table, expenses_table = formatter.format_range_table(
                    expenses_dict, start, end, total, stats
                )
                formatter.print_table(stats_table)
                rprint(f"\n[bold green]💰 Detailed Expenses[/bold green]")
                formatter.print_table(expenses_table)

            except ValueError as e:
                rprint(f"[red]{e}[/red]")
            return

        if date is None:
            date = datetime.today().strftime("%Y-%m-%d")

        if week:
            expenses_dict = expense_service.get_expenses_by_week()
            total = 0.0
            for day, expenses in expenses_dict.items():
                day_total = sum(float(e["amount"]) for e in expenses)
                total += day_total
                if expenses:
                    table = formatter.format_expenses_table(expenses, day)
                    formatter.print_table(table)
                    rprint("_____________________________")
            rprint(f'[bold green]Final Total:[/bold green] [bold purple]{total:,.2f}[/bold purple]')
        else:
            expenses = expense_service.get_expenses_by_date(date)
            table = formatter.format_expenses_table(expenses, date)
            formatter.print_table(table)

    @app.command()
    def edit(
        date: str = typer.Argument(..., help="Date of the expense (YYYY-MM-DD)"),
        identifier: str = typer.Argument(..., help="Expense name or index number"),
        expense: Optional[str] = typer.Option(None, "--expense", "-e", help="New expense name"),
        amount: Optional[float] = typer.Option(None, "--amount", "-a", help="New amount"),
    ):
        """
        Edit an existing expense by date and name/index.

        Examples:
            ledger edit 2025-07-15 0 --expense "Groceries" --amount 150.0
            ledger edit 2025-07-15 "lunch" --amount 25.0
        """
        if not expense and not amount:
            rprint("[red]At least one of --expense or --amount must be provided.[/red]")
            return

        try:
            # Try to convert identifier to int (index), otherwise use as string (name)
            try:
                identifier = int(identifier)
            except ValueError:
                pass  # Keep as string

            expense_service.update_expense(date, identifier, expense, amount)
            rprint("[bold green]Expense edited successfully.[/bold green]")

        except ValueError as e:
            rprint(f"[red]{e}[/red]")
        except Exception as e:
            rprint(f"[red]Error editing expense: {e}[/red]")

    @app.command()
    def delete(
        date: str = typer.Argument(..., help="Date of the expense (YYYY-MM-DD)"),
        identifier: str = typer.Argument(..., help="Expense name or index number"),
    ):
        """
        Delete an expense by date and name/index.

        Examples:
            ledger delete 2025-07-15 0
            ledger delete 2025-07-15 "lunch"
        """
        try:
            # Try to convert identifier to int (index), otherwise use as string (name)
            try:
                identifier = int(identifier)
            except ValueError:
                pass  # Keep as string

            confirm = typer.confirm(f"Are you sure you want to delete the expense on {date}?")
            if confirm:
                expense_service.delete_expense(date, identifier)
                rprint("[bold green]Expense deleted successfully.[/bold green]")
            else:
                rprint("[yellow]Deletion cancelled.[/yellow]")

        except ValueError as e:
            rprint(f"[red]{e}[/red]")
        except Exception as e:
            rprint(f"[red]Error deleting expense: {e}[/red]")

    @app.command()
    def clear():
        """Clear all expenses from the ledger."""
        confirm = typer.confirm("Are you sure you want to clear all expenses? This cannot be undone.")
        if confirm:
            expense_service.delete_all()
            rprint("[green]Ledger cleared successfully.[/green]")
        else:
            rprint("[yellow]Clear operation cancelled.[/yellow]")

