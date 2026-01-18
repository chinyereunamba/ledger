"""Natural Language Processing routes for expense parsing."""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from datetime import datetime
from pydantic import BaseModel

from ..dependencies import get_expense_service
from ...ledger.services.expense_service import ExpenseService
from ...ledger.parsers.nlp_parser import parse_and_enhance


router = APIRouter(prefix="/nlp", tags=["nlp"])


class NaturalLanguageInput(BaseModel):
    """Request model for natural language input."""

    text: str


@router.post("/parse", response_model=List[Dict[str, Any]])
async def parse_natural_language(input_data: NaturalLanguageInput):
    """
    Parse natural language text to extract expenses.

    Example input: "Bought airtime for 500 and lunch for 1500"
    Returns: [{"expense": "airtime", "amount": 500}, {"expense": "lunch", "amount": 1500}]
    """
    try:
        parsed_expenses = parse_and_enhance(input_data.text)

        if not parsed_expenses:
            raise HTTPException(
                status_code=400, detail="Could not parse any expenses from the input text"
            )

        return parsed_expenses

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing natural language: {str(e)}")


@router.post("/say", response_model=Dict[str, Any])
async def say_expenses(
    input_data: NaturalLanguageInput,
    expense_service: ExpenseService = Depends(get_expense_service),
):
    """
    Parse natural language and add expenses to the ledger.

    Example: "Bought airtime for 500 and lunch for 1500"
    """
    try:
        # Parse the natural language input
        parsed_expenses = parse_and_enhance(input_data.text)

        if not parsed_expenses:
            raise HTTPException(
                status_code=400, detail="Could not parse any expenses from the input text"
            )

        # Add expenses
        added_expenses = []
        for expense_data in parsed_expenses:
            expense = expense_service.add_expense(
                expense_data["expense"], expense_data["amount"]
            )
            added_expenses.append({
                "expense": expense.expense,
                "amount": expense.amount,
            })

        return {
            "message": f"Successfully added {len(added_expenses)} expense(s)",
            "original_text": input_data.text,
            "parsed_expenses": added_expenses,
            "date": datetime.now().strftime("%Y-%m-%d"),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing natural language input: {str(e)}"
        )

