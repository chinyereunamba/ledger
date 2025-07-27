from ledger.ledger import (add_expense, all_time, delete_all, get_stats, get_summary_by_date,
    get_summary_by_week, json_to_csv)
import typer
from typing import Optional
from rich import print
from datetime import datetime
from ledger.user import delete_user, get_user


app = typer.Typer(rich_markup_mode='rich')


@app.command()
def view(
    date: Optional[str] = None,
    week: bool = False,
):
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
def summary(all: bool = False):
    """
    Display a summary of expenses.

    Args:
        all (bool): If True, display a summary of all expenses. Defaults to False.
    """
    if all:
        all_time()


@app.command()
def export(csv: bool = False):
    """
    Export the ledger data to a CSV file.

    Args:
        csv (bool): If True, export the data to a CSV file. Defaults to False.
    """
    if csv:
        json_to_csv()


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

    This is a simple command-line tool to help you track your daily expenses.

    🧾 Available commands:
    - [bold cyan]add[/bold cyan]: Add a new expense to your ledger
    - [bold cyan]stats[/bold cyan]: View total spending by category
    - [bold cyan]show[/bold cyan]: View all expenses
    - [bold cyan]clear[/bold cyan]: Reset the ledger

    👉 Type [bold yellow]ledger [command]--help[/bold yellow] to get help on any command.
    """
    if ctx.invoked_subcommand is None:
        print("[bold green]📒 Welcome to Ledger![/bold green]")
        print("Track your daily expenses easily right from your terminal.\n")
        print("🧾 [bold]Available commands:[/bold]")
        print("  • [cyan]add[/cyan]    - Add a new expense")
        print("  • [cyan]stats[/cyan]  - View stats by expense type")
        print("  • [cyan]show[/cyan]   - Show all saved expenses")
        print("  • [cyan]clear[/cyan]  - Clear the ledger\n")
        print("👉 Type [yellow]ledger COMMAND --help[/yellow] for usage details.\n")
        get_user()


@app.command()
def clear():
    delete_all()

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
