from ledger.ledger import (add_expense, all_time, get_summary_by_date, get_summary_by_week,
    json_to_csv)
import typer
from typing import Optional
from rich import print

app = typer.Typer()


@app.command()
def view(
    date: Optional[str] = None,
    week: bool = False,
):
    total = 0
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
def add(expense: Optional[str] = None, amount: Optional[float] = None):
    if not expense:
        expense = typer.prompt("What did you buy today?")
    if not amount:
        amount = typer.prompt(f"How much did you spend on {expense.title()}")

    add_expense(expense, amount)

@app.command()
def summary(all:bool=False):
    if all:
        all_time()

@app.command()
def export(csv:bool=False):
    if csv:
        json_to_csv()

if __name__ == "__main__":
    app()
