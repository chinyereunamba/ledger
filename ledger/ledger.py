from typing import Optional
from datetime import datetime, timedelta
import json
from rich import print
from rich.table import Table
from rich.console import Console
import csv
import pandas as pd 
from pathlib import Path

LEDGER = Path("ledger.json")


def load_ledger(mode: str):
    try:
        return open("ledger.json", mode)
    except FileNotFoundError:
        if mode == "r":
            return open("ledger.json", "w+")
        raise


def add_expense(expense: Optional[str], amount: Optional[float]):

    date_key = datetime.now().strftime("%Y-%m-%d")
    expense_item = {
        "expense": expense,
        "amount": amount,
    }
    # Try to load existing data
    f = load_ledger("r")
    data = json.load(f)

    # Add expense under the date
    if date_key not in data:
        data[date_key] = []

    data[date_key].append(expense_item)

    # Save back to file
    f = load_ledger("w")
    json.dump(data, f, indent=2)

    print("✅ Expense saved successfully.")


console = Console()


def get_summary_by_date(date: str):
    f = load_ledger("r")
    data = json.load(f)
    total = 0
    if date == datetime.today().strftime("%Y-%m-%d"):
        print(f"\nToday's summary: {date}")
    else:
        print(f"\nSummary for {date}")

    table = Table("Expense", "amount".title())
    if date in data:
        for expense in data[date]:
            total += int(expense["amount"])
            table.add_row(
                str(expense['expense']).title(), str(expense['amount']))

        table.add_row('Total', f"{total:,}")

        console.print(table)

    else:
        print("\nNo expense found for this date")

    return total


def get_summary_by_week():
    today_date = datetime.today()
    date_list = [(today_date + timedelta(days=i)).strftime("%Y-%m-%d")
                 for i in range(-6, 1)]
    return date_list

def all_time():
    f = load_ledger("r")
    data = json.load(f)
    total = 0

    table = Table("Date", "Expense", "Amount")

    for date, expenses in data.items():  # Use .items() to get key-value pairs
        for expense in expenses:
            table.add_row(date, expense["expense"], f"{expense['amount']}")
            total += int(expense["amount"])  # Ensure amount is treated as an integer

    table.add_row("", "[bold green]Total Expenditure[/bold green]", f"[bold green]{total:,}[/bold green]")
    console.print(table)




def get_category(category: str):
    f = load_ledger("r")
    data = json.load(f)

    for item in data:
        pass

def json_to_csv():
    # Load the JSON data
    with open(LEDGER, "r") as f:
        data = json.load(f)

    # Flatten the data
    flattened_data = []
    for date, expenses in data.items():
        for expense in expenses:
            flattened_data.append({
                "Date": date,
                "Expense": expense["expense"],
                "Amount": expense["amount"]
            })

    # Convert to a DataFrame
    df = pd.DataFrame(flattened_data)

    # Write the DataFrame to a CSV file
    df.to_csv("output.csv", encoding='utf-8', index=False)
    print("✅ Exported to output.csv successfully.")