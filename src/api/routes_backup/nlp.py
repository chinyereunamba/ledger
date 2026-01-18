"""
Natural Language Processing routes for expense parsing
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from datetime import datetime
import json

from pydantic import BaseModel
from models import ExpenseCreate
from utils import load_ledger_data

# Import ledger and NLP functions
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ledger.ledger import LEDGER
from ledger.nlp_parser import parse_and_enhance

router = APIRouter(prefix="/nlp", tags=["nlp"])

class NaturalLanguageInput(BaseModel):
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
                status_code=400, 
                detail="Could not parse any expenses from the input text"
            )
        
        return parsed_expenses
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing natural language: {str(e)}")

@router.post("/say", response_model=Dict[str, Any])
async def say_expenses(input_data: NaturalLanguageInput):
    """
    Parse natural language and add expenses to the ledger.
    
    Example: "Bought airtime for 500 and lunch for 1500"
    """
    try:
        # Parse the natural language input
        parsed_expenses = parse_and_enhance(input_data.text)
        
        if not parsed_expenses:
            raise HTTPException(
                status_code=400,
                detail="Could not parse any expenses from the input text"
            )
        
        # Get current date
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        # Load existing data
        data = load_ledger_data()
        
        # Add expenses to the current date
        if current_date not in data:
            data[current_date] = []
        
        added_expenses = []
        for expense_data in parsed_expenses:
            expense_item = {
                "expense": expense_data["expense"].lower(),
                "amount": expense_data["amount"]
            }
            data[current_date].append(expense_item)
            added_expenses.append(expense_item)
        
        # Save back to file
        with open(LEDGER, "w") as f:
            json.dump(data, f, indent=2)
        
        return {
            "message": f"Successfully added {len(added_expenses)} expense(s)",
            "original_text": input_data.text,
            "parsed_expenses": added_expenses,
            "date": current_date
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing natural language input: {str(e)}")