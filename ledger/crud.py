from enum import Enum


LEDGER = "/.ledger"


def add(expense: str, amount: int) -> None:
    """Create a new expense"""
    expense_name = expense.title()
    amount_spent = float(amount)

    print(expense_name, amount_spent)


def read()-> None:
    """Read all expenses"""
    pass

def update()-> None:
    """Update an expense"""
    pass

def delete(id: int)-> None:
    """Delete an expense"""
    pass
