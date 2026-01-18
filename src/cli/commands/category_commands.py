"""CLI commands for category management."""

import typer
from typing import Optional
from rich import print as rprint

from ...ledger.services import CategoryService
from ..presenters import TableFormatter


def register_category_commands(app: typer.Typer, category_service: CategoryService):
    """Register category-related CLI commands."""

    formatter = TableFormatter()

    @app.command()
    def categories(
        action: Optional[str] = typer.Argument(None, help="Action: list, add, remove, update, summary"),
        category: Optional[str] = typer.Option(None, "--category", "-c", help="Category name"),
        keywords: Optional[str] = typer.Option(None, "--keywords", "-k", help="Comma-separated keywords"),
    ):
        """
        Manage expense categories.

        Examples:
            ledger categories list
            ledger categories summary
            ledger categories add --category "travel" --keywords "flight,hotel,taxi"
            ledger categories remove --category "travel"
            ledger categories update --category "food" --keywords "lunch,dinner,snacks"
        """
        try:
            if action == "summary":
                from ...ledger.services import ExpenseService
                expense_service = ExpenseService()
                expenses_dict = expense_service.get_all_expenses()
                category_totals = category_service.get_category_summary(expenses_dict)

                rprint("\n[bold blue]💰 Spending by Category[/bold blue]")
                table = formatter.format_category_table(category_totals)
                formatter.print_table(table)

            elif action in ["add", "remove", "update"]:
                if not category:
                    rprint(f"[red]Category name is required for {action} action.[/red]")
                    return

                keyword_list = None
                if keywords:
                    keyword_list = [k.strip() for k in keywords.split(",")]

                if action == "add":
                    category_service.add_category(category, keyword_list)
                    rprint(f"[green]Added category '{category}' with keywords: {keyword_list or 'none'}[/green]")

                elif action == "remove":
                    category_service.remove_category(category)
                    rprint(f"[green]Removed category '{category}'[/green]")

                elif action == "update":
                    if not keyword_list:
                        rprint("[red]Keywords are required for update action.[/red]")
                        return
                    category_service.update_category(category, keyword_list)
                    rprint(f"[green]Updated category '{category}' with keywords: {keyword_list}[/green]")

            else:
                # List categories
                categories = category_service.get_all_categories()
                rprint("\n[bold blue]📂 Expense Categories[/bold blue]")
                categories_dict = {name: cat.keywords for name, cat in categories.items()}
                table = formatter.format_categories_list_table(categories_dict)
                formatter.print_table(table)

        except ValueError as e:
            rprint(f"[red]{e}[/red]")
        except Exception as e:
            rprint(f"[red]Error managing categories: {e}[/red]")

