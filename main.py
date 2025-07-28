from ledger.ledger import (
    add_expense, all_time, delete_all, get_stats, get_summary_by_date,
    get_summary_by_week, json_to_csv, get_summary, edit_expense, 
    delete_expense, manage_categories, get_category_summary, view_range,
    show_backups, get_ledger_info, LEDGER
)
from ledger.nlp_parser import parse_and_enhance
import typer
from typing import Optional
from rich import print
from datetime import datetime
from ledger.user import delete_user, get_user
import json


app = typer.Typer(rich_markup_mode='rich')


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
    # Range view takes priority
    if start or end:
        if not start:
            print("[red]Start date is required when using date range.[/red]")
            return
        if not end:
            print("[red]End date is required when using date range.[/red]")
            return
        view_range(start, end)
        return
    
    total = 0
    if date is None:
        date = datetime.today().strftime("%Y-%m-%d")
    
    if week:
        dates = get_summary_by_week()
        for day in dates:
            sum = get_summary_by_date(day)
            total += sum
            print("_____________________________")
        print(
            f'[bold green]Final Total:[/bold green] [bold purple]{total:,}[/bold purple]')
    else:
        get_summary_by_date(date)


@app.command()
def add(
    expense: Optional[str] = typer.Argument(None),
    amount: Optional[float] = typer.Argument(None)
):
    """
    Add expenses to the ledger via CLI arguments or interactive prompts.
    """
    while True:
        if not expense:
            expense = typer.prompt("What did you buy today?")

        if not amount:
            amount = typer.prompt(
                f"How much did you spend on {expense.title()}")

        try:
            amount = float(amount)
        except ValueError:
            print("[red]Amount must be a number. Try again.[/red]")
            expense = None
            amount = None
            continue

        add_expense(expense, amount)

        # Reset so user can enter a new expense interactively
        expense = None
        amount = None

        done = typer.confirm("Would that be all?")
        if done:
            break

    print("[bold green]All expenses added![/bold green]")


@app.command()
def summary(
    all: bool = False,
    start: Optional[str] = None,
    end: Optional[str] = None
):
    """
    Display a summary of expenses.

    Args:
        all: Show all-time summary.
        start: Start date for range summary (YYYY-MM-DD).
        end: End date for range summary (YYYY-MM-DD).
    """
    if start or end:
        get_summary(start, end)
    elif all:
        all_time()
    else:
        all_time()


@app.command()
def export(
    csv: bool = typer.Option(True, help="Export to CSV format"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output filename")
):
    """
    Export the ledger data to a CSV file.
    
    Examples:
        ledger export
        ledger export --output my_expenses.csv
    """
    if csv:
        json_to_csv(output)


@app.command()
def stats():
    """
    Display statistics about the expenses.

    This function is currently a placeholder and does not perform any operations.
    """
    get_stats()


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """
    Welcome to Ledger!

    A comprehensive command-line tool to track and analyze your daily expenses.
    """
    if ctx.invoked_subcommand is None:
        print("[bold green]📒 Welcome to Ledger![/bold green]")
        print("Track your daily expenses easily right from your terminal.\n")
        
        print("🧾 [bold]Core Commands:[/bold]")
        print("  • [cyan]add[/cyan]        - Add a new expense")
        print("  • [cyan]say[/cyan]        - Add expenses using natural language")
        print("  • [cyan]view[/cyan]       - View expenses by date/range")
        print("  • [cyan]edit[/cyan]       - Edit existing expenses")
        print("  • [cyan]delete[/cyan]     - Delete specific expenses")
        print("  • [cyan]stats[/cyan]      - View comprehensive analytics")
        print("  • [cyan]summary[/cyan]    - Show expense summaries")
        print("  • [cyan]categories[/cyan] - Manage expense categories")
        print("  • [cyan]export[/cyan]     - Export data to CSV")
        print("  • [cyan]backups[/cyan]    - View backup files")
        print("  • [cyan]info[/cyan]       - Show ledger information")
        print("  • [cyan]clear[/cyan]      - Clear all expenses")
        print("  • [cyan]user[/cyan]       - User management\n")
        
        print("� [bold]Quick Examples:[/bold]")
        print("  [dim]ledger add \"Coffee\" 5.50[/dim]")
        print("  [dim]ledger say \"Bought airtime for 500 and lunch for 1500\"[/dim]")
        print("  [dim]ledger view --start 2025-07-01 --end 2025-07-20[/dim]")
        print("  [dim]ledger stats[/dim]")
        print("  [dim]ledger categories summary[/dim]\n")
        
        print("👉 Type [yellow]ledger COMMAND --help[/yellow] for detailed usage.\n")
        
        # Show ledger status and quick stats if data exists
        if LEDGER.exists():
            try:
                with open(LEDGER, "r") as f:
                    data = json.load(f)
                if data:
                    total_expenses = sum(len(expenses) for expenses in data.values())
                    print(f"📈 [bold green]Current Status:[/bold green] {len(data)} days tracked, {total_expenses} transactions")
                else:
                    print("📝 [dim]No expenses recorded yet. Start with 'ledger add'![/dim]")
            except:
                print("📝 [dim]Ready to track your expenses![/dim]")
        else:
            print("📝 [dim]Welcome! Your ledger will be created at ~/.ledger/ when you add your first expense.[/dim]")
        
       


@app.command()
def edit(
    date: str = typer.Argument(..., help="Date of the expense (YYYY-MM-DD)"),
    identifier: str = typer.Argument(..., help="Expense name or index number"),
    expense: Optional[str] = typer.Option(None, "--expense", "-e", help="New expense name"),
    amount: Optional[float] = typer.Option(None, "--amount", "-a", help="New amount")
):
    """
    Edit an existing expense by date and name/index.
    
    Examples:
        ledger edit 2025-07-15 0 --expense "Groceries" --amount 150.0
        ledger edit 2025-07-15 "lunch" --amount 25.0
    """
    if not expense and not amount:
        print("[red]At least one of --expense or --amount must be provided.[/red]")
        return
    
    # Try to convert identifier to int (index), otherwise use as string (name)
    try:
        identifier = int(identifier)
    except ValueError:
        pass  # Keep as string
    
    edit_expense(date, identifier, expense, amount)


@app.command()
def delete(
    date: str = typer.Argument(..., help="Date of the expense (YYYY-MM-DD)"),
    identifier: str = typer.Argument(..., help="Expense name or index number")
):
    """
    Delete an expense by date and name/index.
    
    Examples:
        ledger delete 2025-07-15 0
        ledger delete 2025-07-15 "lunch"
    """
    # Try to convert identifier to int (index), otherwise use as string (name)
    try:
        identifier = int(identifier)
    except ValueError:
        pass  # Keep as string
    
    confirm = typer.confirm(f"Are you sure you want to delete the expense on {date}?")
    if confirm:
        delete_expense(date, identifier)
    else:
        print("[yellow]Deletion cancelled.[/yellow]")


@app.command()
def categories(
    action: Optional[str] = typer.Argument(None, help="Action: list, add, remove, update, summary"),
    category: Optional[str] = typer.Option(None, "--category", "-c", help="Category name"),
    keywords: Optional[str] = typer.Option(None, "--keywords", "-k", help="Comma-separated keywords")
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
    if action == "summary":
        get_category_summary()
    elif action in ["add", "remove", "update"]:
        if not category:
            print(f"[red]Category name is required for {action} action.[/red]")
            return
        
        keyword_list = None
        if keywords:
            keyword_list = [k.strip() for k in keywords.split(",")]
        
        manage_categories(action, category, keyword_list)
    else:
        # Default to list if no action or "list" action
        manage_categories("list")


@app.command()
def backups():
    """Show available backup files."""
    show_backups()


@app.command()
def info():
    """Show ledger configuration and file information."""
    get_ledger_info()


@app.command()
def say(input_text: str = typer.Argument(..., help="Natural language expense input")):
    """
    Add expenses using natural language.
    
    Examples:
        ledger say "Bought airtime for 500 and lunch for 1500"
        ledger say "Paid transport 800, airtime 300"
        ledger say "Spent 200 on coffee and 150 on snacks"
    """
    try:
        # Parse the natural language input
        parsed_expenses = parse_and_enhance(input_text)
        
        if not parsed_expenses:
            print("[yellow]Could not parse any expenses from the input. Please try a different format.[/yellow]")
            print("\n[dim]Examples:[/dim]")
            print("  [dim]ledger say \"Bought airtime for 500 and lunch for 1500\"[/dim]")
            print("  [dim]ledger say \"Transport 800, airtime 300\"[/dim]")
            print("  [dim]ledger say \"Spent 200 on coffee\"[/dim]")
            return
        
        # Show what was parsed
        print(f"[blue]Parsed {len(parsed_expenses)} expense(s) from:[/blue] \"{input_text}\"")
        print()
        
        # Add each expense
        for expense_data in parsed_expenses:
            add_expense(expense_data["expense"], expense_data["amount"])
            print(f"✅ Added: {expense_data['expense']} - ₦{expense_data['amount']}")
        
        print(f"\n[bold green]Successfully added {len(parsed_expenses)} expense(s)![/bold green]")
        
    except Exception as e:
        print(f"[red]Error processing natural language input: {e}[/red]")


@app.command()
def clear():
    """Clear all expenses from the ledger."""
    confirm = typer.confirm("Are you sure you want to clear all expenses? This cannot be undone.")
    if confirm:
        delete_all()
        print("[green]Ledger cleared successfully.[/green]")
    else:
        print("[yellow]Clear operation cancelled.[/yellow]")

user = typer.Typer()
app.add_typer(user, name='user')


@user.command('delete')
def delete():
    sure = typer.confirm('are you sure you want to delete user?')
    if sure:
        delete_user()
    else:
        typer.Exit()


if __name__ == "__main__":
    app()
