from typing import Optional
from datetime import datetime, timedelta
import json
import os
import shutil
from rich import print
from rich.table import Table
from rich.console import Console
import csv
import pandas as pd
from pathlib import Path

# Use hidden config folder in user's home directory
LEDGER_DIR = Path.home() / ".ledger"
LEDGER = LEDGER_DIR / "ledger.json"
BACKUP_DIR = LEDGER_DIR / "backups"


def ensure_ledger_directory():
    """Create ledger directory and subdirectories if they don't exist."""
    LEDGER_DIR.mkdir(exist_ok=True)
    BACKUP_DIR.mkdir(exist_ok=True)


def create_backup():
    """Create a backup of the current ledger file."""
    if LEDGER.exists():
        ensure_ledger_directory()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = BACKUP_DIR / f"ledger_backup_{timestamp}.json"
        shutil.copy2(LEDGER, backup_file)

        # Keep only the last 10 backups
        backups = sorted(BACKUP_DIR.glob("ledger_backup_*.json"))
        if len(backups) > 10:
            for old_backup in backups[:-10]:
                old_backup.unlink()

        return backup_file
    return None


def load_ledger(mode: str):
    """Load ledger file with auto-creation and backup support."""
    ensure_ledger_directory()

    try:
        if mode == "w" and LEDGER.exists():
            # Create backup before writing
            backup_file = create_backup()
            if backup_file:
                print(f"[dim]Backup created: {backup_file.name}[/dim]")

        return open(LEDGER, mode)
    except FileNotFoundError:
        if mode == "r":
            # Create empty ledger file if it doesn't exist
            LEDGER.write_text("{}")
            return open(LEDGER, mode)
        raise


def add_expense(expense: Optional[str], amount: Optional[float]):

    date_key = datetime.now().strftime("%Y-%m-%d")
    expense_item = {
        "expense": expense,
        "amount": amount,
    }

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
                str(expense["expense"]).title(), str(expense["amount"]))

        table.add_row("Total", f"{total:,}")

        console.print(table)

    else:
        print("\nNo expense found for this date")

    return total


def get_summary_by_week():
    today_date = datetime.today()
    date_list = [
        (today_date + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(-6, 1)
    ]
    return date_list


def view_range(start_date, end_date):
    """
    View expenses within a specific date range.
    Usage: ledger view --start 2025-07-01 --end 2025-07-20

    Args:
        start_date (str): Start date in YYYY-MM-DD format
        end_date (str): End date in YYYY-MM-DD format
    """
    try:
        f = load_ledger("r")
        data = json.load(f)
    except Exception as e:
        print(f"[red]Error loading ledger: {e}[/red]")
        return

    if not data:
        print("[yellow]No expenses found in ledger.[/yellow]")
        return

    # Validate date format
    try:
        from datetime import datetime
        datetime.strptime(start_date, "%Y-%m-%d")
        datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        print("[red]Invalid date format. Use YYYY-MM-DD format.[/red]")
        return

    if start_date > end_date:
        print("[red]Start date cannot be after end date.[/red]")
        return

    total = 0
    filtered_data = {}
    transaction_count = 0

    for date, expenses in data.items():
        if start_date <= date <= end_date:
            filtered_data[date] = expenses
            transaction_count += len(expenses)

    if not filtered_data:
        print(
            f"[yellow]No expenses found between {start_date} and {end_date}.[/yellow]")
        return

    # Calculate some quick stats
    daily_totals = {}
    category_totals = {}

    for date, expenses in filtered_data.items():
        daily_total = 0
        for expense in expenses:
            amount = float(expense["amount"])
            daily_total += amount
            total += amount

            # Categorize expense
            category = get_expense_category(expense["expense"])
            if category not in category_totals:
                category_totals[category] = 0
            category_totals[category] += amount

        daily_totals[date] = daily_total

    # Display header with range info
    print(
        f"\n[bold blue]📅 Expenses from {start_date} to {end_date}[/bold blue]")
    print("=" * 60)

    # Quick stats
    days_with_expenses = len(filtered_data)
    avg_daily = total / days_with_expenses if days_with_expenses > 0 else 0
    max_day = max(daily_totals.items(),
                  key=lambda x: x[1]) if daily_totals else ("", 0)
    top_category = max(category_totals.items(),
                       key=lambda x: x[1]) if category_totals else ("", 0)

    stats_table = Table("Metric", "Value", title="📊 Range Summary")
    stats_table.add_row("Total Spent", f"₦{total:,.2f}")
    stats_table.add_row("Days with Expenses", str(days_with_expenses))
    stats_table.add_row("Total Transactions", str(transaction_count))
    stats_table.add_row("Average per Day", f"₦{avg_daily:,.2f}")
    stats_table.add_row("Highest Spending Day",
                        f"{max_day[0]} (₦{max_day[1]:,.2f})")
    stats_table.add_row(
        "Top Category", f"{top_category[0].title()} (₦{top_category[1]:,.2f})")
    console.print(stats_table)

    # Detailed expenses table
    print(f"\n[bold green]💰 Detailed Expenses[/bold green]")
    expenses_table = Table("Date", "Expense", "Amount", "Category")

    for date in sorted(filtered_data.keys()):
        expenses = filtered_data[date]
        for expense in expenses:
            category = get_expense_category(expense["expense"])
            expenses_table.add_row(
                date,
                expense["expense"],
                f"₦{expense['amount']}",
                category.title()
            )

    expenses_table.add_row(
        "",
        "[bold green]Total for Range[/bold green]",
        f"[bold green]₦{total:,.2f}[/bold green]",
        ""
    )
    console.print(expenses_table)

    return {
        'total': total,
        'days_with_expenses': days_with_expenses,
        'transaction_count': transaction_count,
        'avg_daily': avg_daily,
        'daily_totals': daily_totals,
        'category_totals': category_totals
    }


def get_summary(start_date=None, end_date=None):
    """
    Show summary for all-time or specific date range.
    Args:
        start_date (str): Start date in YYYY-MM-DD format (optional)
        end_date (str): End date in YYYY-MM-DD format (optional)
    """
    try:
        f = load_ledger("r")
        data = json.load(f)
    except Exception as e:
        print(f"[red]Error loading ledger: {e}[/red]")
        return

    if not data:
        print("[yellow]No expenses found in ledger.[/yellow]")
        return

    total = 0
    filtered_data = {}

    # Filter by date range if provided
    for date, expenses in data.items():
        include_date = True

        if start_date and date < start_date:
            include_date = False
        if end_date and date > end_date:
            include_date = False

        if include_date:
            filtered_data[date] = expenses

    if not filtered_data:
        date_range = f" from {start_date} to {end_date}" if start_date or end_date else ""
        print(f"[yellow]No expenses found{date_range}.[/yellow]")
        return

    # Display title
    if start_date or end_date:
        title = f"Summary from {start_date or 'beginning'} to {end_date or 'now'}"
    else:
        title = "All-Time Summary"

    print(f"\n[bold blue]{title}[/bold blue]")

    table = Table("Date", "Expense", "Amount")

    for date, expenses in sorted(filtered_data.items()):
        for expense in expenses:
            table.add_row(date, expense["expense"], f"₦{expense['amount']}")
            total += float(expense["amount"])

    table.add_row(
        "",
        "[bold green]Total Expenditure[/bold green]",
        f"[bold green]₦{total:,.2f}[/bold green]",
    )
    console.print(table)
    return total


def all_time():
    """Legacy function - redirects to get_summary()"""
    return get_summary()


CATEGORIES_FILE = LEDGER_DIR / "categories.json"


def load_categories():
    """Load expense categories from file"""
    ensure_ledger_directory()

    try:
        with open(CATEGORIES_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        # Default categories
        default_categories = {
            "food": ["lunch", "dinner", "breakfast", "snacks", "groceries", "restaurant"],
            "transport": ["fuel", "taxi", "bus", "train", "uber", "transport"],
            "utilities": ["electricity", "water", "internet", "phone", "gas"],
            "entertainment": ["movie", "games", "music", "books", "streaming"],
            "health": ["medicine", "doctor", "hospital", "pharmacy", "fitness"],
            "shopping": ["clothes", "electronics", "household", "gifts"],
            "education": ["books", "courses", "tuition", "training"],
            "miscellaneous": []
        }
        save_categories(default_categories)
        return default_categories


def save_categories(categories):
    """Save categories to file with backup"""
    ensure_ledger_directory()

    # Create backup if file exists
    if CATEGORIES_FILE.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = BACKUP_DIR / f"categories_backup_{timestamp}.json"
        shutil.copy2(CATEGORIES_FILE, backup_file)

    with open(CATEGORIES_FILE, "w") as f:
        json.dump(categories, f, indent=2)


def get_expense_category(expense_name):
    """Determine category for an expense based on keywords"""
    categories = load_categories()
    expense_lower = expense_name.lower()

    for category, keywords in categories.items():
        if any(keyword in expense_lower for keyword in keywords):
            return category

    return "miscellaneous"


def manage_categories(action=None, category=None, keywords=None):
    """
    Manage expense categories
    Args:
        action: 'list', 'add', 'remove', 'update'
        category: category name
        keywords: list of keywords for the category
    """
    categories = load_categories()

    if action == "list" or action is None:
        print("\n[bold blue]📂 Expense Categories[/bold blue]")
        table = Table("Category", "Keywords")
        for cat, words in categories.items():
            keywords_str = ", ".join(
                words) if words else "[dim]No keywords[/dim]"
            table.add_row(cat.title(), keywords_str)
        console.print(table)

    elif action == "add":
        if not category:
            print("[red]Category name required for add action[/red]")
            return

        if category in categories:
            print(f"[yellow]Category '{category}' already exists[/yellow]")
            return

        categories[category] = keywords or []
        save_categories(categories)
        print(
            f"[green]Added category '{category}' with keywords: {keywords or 'none'}[/green]")

    elif action == "remove":
        if not category:
            print("[red]Category name required for remove action[/red]")
            return

        if category not in categories:
            print(f"[yellow]Category '{category}' not found[/yellow]")
            return

        del categories[category]
        save_categories(categories)
        print(f"[green]Removed category '{category}'[/green]")

    elif action == "update":
        if not category:
            print("[red]Category name required for update action[/red]")
            return

        if category not in categories:
            print(f"[yellow]Category '{category}' not found[/yellow]")
            return

        categories[category] = keywords or []
        save_categories(categories)
        print(
            f"[green]Updated category '{category}' with keywords: {keywords or 'none'}[/green]")


def get_category_summary():
    """Show expenses grouped by categories"""
    try:
        f = load_ledger("r")
        data = json.load(f)
    except Exception as e:
        print(f"[red]Error loading ledger: {e}[/red]")
        return

    if not data:
        print("[yellow]No expenses found in ledger.[/yellow]")
        return

    category_totals = {}

    # Categorize all expenses
    for date, expenses in data.items():
        for expense in expenses:
            category = get_expense_category(expense["expense"])
            if category not in category_totals:
                category_totals[category] = 0
            category_totals[category] += float(expense["amount"])

    # Sort by amount
    sorted_categories = sorted(
        category_totals.items(), key=lambda x: x[1], reverse=True)
    total_spent = sum(category_totals.values())

    print("\n[bold blue]💰 Spending by Category[/bold blue]")
    table = Table("Category", "Amount", "Percentage")

    for category, amount in sorted_categories:
        percentage = (amount / total_spent) * 100 if total_spent > 0 else 0
        table.add_row(
            category.title(),
            f"₦{amount:,.2f}",
            f"{percentage:.1f}%"
        )

    table.add_row(
        "[bold]Total[/bold]",
        f"[bold]₦{total_spent:,.2f}[/bold]",
        "[bold]100.0%[/bold]"
    )

    console.print(table)
    return category_totals


def json_to_csv(output_file=None):
    """Export ledger data to CSV with enhanced features."""
    try:
        with open(LEDGER, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("[red]No ledger file found.[/red]")
        return

    if not data:
        print("[yellow]No expenses to export.[/yellow]")
        return

    # Flatten the data with categories
    flattened_data = []
    for date, expenses in data.items():
        for expense in expenses:
            category = get_expense_category(expense["expense"])
            flattened_data.append({
                "Date": date,
                "Expense": expense["expense"],
                "Amount": expense["amount"],
                "Category": category.title()
            })

    # Convert to a DataFrame
    df = pd.DataFrame(flattened_data)

    # Generate filename if not provided
    if not output_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"ledger_export_{timestamp}.csv"

    # Write the DataFrame to a CSV file
    df.to_csv(output_file, encoding="utf-8", index=False)

    # Show summary
    total_amount = df['Amount'].astype(float).sum()
    print(f"✅ Exported {len(df)} transactions to {output_file}")
    print(f"📊 Total amount: ₦{total_amount:,.2f}")


def show_backups():
    """Display available backup files."""
    ensure_ledger_directory()

    ledger_backups = sorted(BACKUP_DIR.glob(
        "ledger_backup_*.json"), reverse=True)
    category_backups = sorted(BACKUP_DIR.glob(
        "categories_backup_*.json"), reverse=True)

    if not ledger_backups and not category_backups:
        print("[yellow]No backup files found.[/yellow]")
        return

    print("\n[bold blue]📁 Available Backups[/bold blue]")

    if ledger_backups:
        print("\n[bold green]Ledger Backups:[/bold green]")
        table = Table("File", "Date Created", "Size")
        for backup in ledger_backups[:10]:  # Show last 10
            stat = backup.stat()
            created = datetime.fromtimestamp(stat.st_mtime)
            size = f"{stat.st_size} bytes"
            table.add_row(backup.name, created.strftime(
                "%Y-%m-%d %H:%M:%S"), size)
        console.print(table)

    if category_backups:
        print("\n[bold yellow]Category Backups:[/bold yellow]")
        table = Table("File", "Date Created", "Size")
        for backup in category_backups[:5]:  # Show last 5
            stat = backup.stat()
            created = datetime.fromtimestamp(stat.st_mtime)
            size = f"{stat.st_size} bytes"
            table.add_row(backup.name, created.strftime(
                "%Y-%m-%d %H:%M:%S"), size)
        console.print(table)

    print(f"\n[dim]Backup location: {BACKUP_DIR}[/dim]")


def get_ledger_info():
    """Display information about the ledger setup."""
    ensure_ledger_directory()

    print("\n[bold blue]📋 Ledger Information[/bold blue]")

    info_table = Table("Setting", "Value")
    info_table.add_row("Ledger Directory", str(LEDGER_DIR))
    info_table.add_row("Ledger File", str(LEDGER))
    info_table.add_row("Categories File", str(CATEGORIES_FILE))
    info_table.add_row("Backup Directory", str(BACKUP_DIR))

    # File existence and sizes
    if LEDGER.exists():
        size = LEDGER.stat().st_size
        info_table.add_row("Ledger Size", f"{size} bytes")
    else:
        info_table.add_row("Ledger Status", "[red]Not created yet[/red]")

    if CATEGORIES_FILE.exists():
        size = CATEGORIES_FILE.stat().st_size
        info_table.add_row("Categories Size", f"{size} bytes")
    else:
        info_table.add_row("Categories Status", "[red]Not created yet[/red]")

    # Count backups
    backup_count = len(list(BACKUP_DIR.glob("*.json")))
    info_table.add_row("Backup Files", str(backup_count))

    console.print(info_table)


def get_stats():
    """
    Show comprehensive analytics including average daily spending, top category, and most expensive day.
    """
    try:
        f = load_ledger("r")
        data = json.load(f)
    except Exception as e:
        print(f"[red]Error loading ledger: {e}[/red]")
        return

    if not data:
        print("[yellow]No expenses found in ledger.[/yellow]")
        return

    # Flatten data for analysis
    records = []
    category_totals = {}

    for date, expenses in data.items():
        for item in expenses:
            records.append({
                "date": date,
                "expense": item["expense"],
                "amount": float(item["amount"])
            })

            # Calculate category totals
            category = get_expense_category(item["expense"])
            if category not in category_totals:
                category_totals[category] = 0
            category_totals[category] += float(item["amount"])

    df = pd.DataFrame(records)

    # Convert date strings to datetime for better analysis
    df['date'] = pd.to_datetime(df['date'])

    # Calculate key statistics
    total_spent = df['amount'].sum()
    total_days = (df['date'].max() - df['date'].min()).days + 1
    avg_daily = total_spent / total_days if total_days > 0 else 0

    # Daily spending totals
    daily_spending = df.groupby('date')['amount'].sum()
    most_expensive_day = daily_spending.idxmax()
    most_expensive_amount = daily_spending.max()

    # Top category
    top_category = max(category_totals.items(), key=lambda x: x[1])

    # Top individual expenses
    top_expenses = df.groupby(
        'expense')['amount'].sum().sort_values(ascending=False)

    print("\n[bold blue]📊 Ledger Statistics[/bold blue]")
    print("=" * 50)

    # Key Highlights
    highlights_table = Table(
        "Key Metric", "Value", title="📈 Key Highlights", title_style="bold magenta")
    highlights_table.add_row("💰 Average Daily Spending", f"₦{avg_daily:,.2f}")
    highlights_table.add_row(
        "🏆 Top Category", f"{top_category[0].title()} (₦{top_category[1]:,.2f})")
    highlights_table.add_row(
        "📅 Most Expensive Day", f"{most_expensive_day.strftime('%Y-%m-%d')} (₦{most_expensive_amount:,.2f})")
    console.print(highlights_table)

    # Overview stats
    overview_table = Table("Metric", "Value", title="📋 Overview")
    overview_table.add_row("Total Spent", f"₦{total_spent:,.2f}")
    overview_table.add_row("Total Days Tracked", str(total_days))
    overview_table.add_row("Total Transactions", str(len(df)))
    overview_table.add_row("Days with Expenses", str(len(daily_spending)))
    console.print(overview_table)

    # Top 5 expense categories by spending
    print("\n[bold green]🏷️ Top 5 Categories[/bold green]")
    top_categories = sorted(category_totals.items(),
                            key=lambda x: x[1], reverse=True)[:5]
    cat_table = Table("Category", "Total Amount", "Percentage")
    for category, amount in top_categories:
        percentage = (amount / total_spent) * 100
        cat_table.add_row(category.title(),
                          f"₦{amount:,.2f}", f"{percentage:.1f}%")
    console.print(cat_table)

    # Top 5 individual expenses
    print("\n[bold yellow]💸 Top 5 Individual Expenses[/bold yellow]")
    expense_table = Table("Expense", "Total Amount")
    for expense, amount in top_expenses.head(5).items():
        expense_table.add_row(expense.title(), f"₦{amount:,.2f}")
    console.print(expense_table)

    return {
        'avg_daily_spending': avg_daily,
        'top_category': top_category,
        'most_expensive_day': (most_expensive_day.strftime('%Y-%m-%d'), most_expensive_amount),
        'total_spent': total_spent,
        'daily_spending': daily_spending,
        'category_totals': category_totals
    }


def delete_all():
    f = load_ledger("w+")
    f.write("{}")


def edit_expense(date, index_or_expense_name, new_expense=None, new_amount=None):
    """
    Edit an expense in the ledger for a given date, by index (int) or expense name (str).
    """
    try:
        f = load_ledger("r")
        data = json.load(f)
    except Exception as e:
        print(f"[red]Error loading ledger: {e}[/red]")
        return

    if date not in data or not data[date]:
        print(f"[yellow]No expenses found for {date}.[/yellow]")
        return

    # Find the expense to edit
    expense_index = None
    if isinstance(index_or_expense_name, int):
        idx = index_or_expense_name
        if 0 <= idx < len(data[date]):
            expense_index = idx
        else:
            print(f"[red]Invalid index: {idx}[/red]")
            return
    else:
        # Find by expense name (case-insensitive, first match)
        for i, item in enumerate(data[date]):
            if str(item["expense"]).lower() == str(index_or_expense_name).lower():
                expense_index = i
                break
        if expense_index is None:
            print(
                f"[yellow]No expense named '{index_or_expense_name}' found on {date}.[/yellow]"
            )
            return

    # Store original values for display
    original_expense = data[date][expense_index]["expense"]
    original_amount = data[date][expense_index]["amount"]

    # Update the expense
    if new_expense is not None:
        data[date][expense_index]["expense"] = new_expense
    if new_amount is not None:
        data[date][expense_index]["amount"] = new_amount

    # Save back to file
    try:
        f = load_ledger("w")
        json.dump(data, f, indent=2)

        # Show what was changed
        updated_expense = data[date][expense_index]["expense"]
        updated_amount = data[date][expense_index]["amount"]

        print(f"[green]Updated expense:[/green]")
        print(f"  From: {original_expense} ₦{original_amount}")
        print(f"  To:   {updated_expense} ₦{updated_amount}")
        print("[bold green]Expense edited successfully.[/bold green]")
    except Exception as e:
        print(f"[red]Error saving ledger: {e}[/red]")


def delete_expense(date, index_or_expense_name):
    """
    Remove an expense from the ledger for a given date, by index (int) or expense name (str).
    """
    try:
        f = load_ledger("r")
        data = json.load(f)
    except Exception as e:
        print(f"[red]Error loading ledger: {e}[/red]")
        return

    if date not in data or not data[date]:
        print(f"[yellow]No expenses found for {date}.[/yellow]")
        return

    # Determine if index_or_expense_name is an int (index) or str (name)
    removed = False
    if isinstance(index_or_expense_name, int):
        idx = index_or_expense_name
        if 0 <= idx < len(data[date]):
            removed_item = data[date].pop(idx)
            removed = True
            print(
                f"[green]Removed:[/green] {removed_item['expense']} ₦{removed_item['amount']}"
            )
        else:
            print(f"[red]Invalid index: {idx}[/red]")
            return
    else:
        # Remove by expense name (case-insensitive, first match)
        for i, item in enumerate(data[date]):
            if str(item["expense"]).lower() == str(index_or_expense_name).lower():
                removed_item = data[date].pop(i)
                removed = True
                print(
                    f"[green]Removed:[/green] {removed_item['expense']} ₦{removed_item['amount']}"
                )
                break
        if not removed:
            print(
                f"[yellow]No expense named '{index_or_expense_name}' found on {date}.[/yellow]"
            )
            return

    # If the date now has no expenses, remove the date key
    if not data[date]:
        del data[date]

    # Save back to file
    try:
        f = load_ledger("w")
        json.dump(data, f, indent=2)
        print("[bold green]Expense deleted successfully.[/bold green]")
    except Exception as e:
        print(f"[red]Error saving ledger: {e}[/red]")
