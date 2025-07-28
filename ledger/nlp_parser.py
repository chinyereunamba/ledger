"""
Natural Language Processing for expense parsing
Allows users to input expenses in natural language like:
"Bought airtime for 500 and lunch for 1500"
"""
import re
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class ParsedExpense:
    expense: str
    amount: float

def parse_natural_expenses(input_text: str) -> List[Dict[str, Any]]:
    """
    Parse natural language input to extract expenses and amounts.
    
    Examples:
    - "Bought airtime for 500 and lunch for 1500"
    - "Paid transport 800, airtime 300"
    - "Spent ₦200 on coffee and ₦150 on snacks"
    - "Food 1200, transport 500, airtime 300"
    """
    expenses = []
    
    # Clean and normalize input
    text = input_text.lower().strip()
    
    # Remove common currency symbols and normalize
    text = re.sub(r'[₦$£€]', '', text)
    
    # Pattern 1: "item for amount" or "item amount"
    # Matches: "airtime for 500", "lunch 1500", "transport for 800"
    pattern1 = r'(\w+(?:\s+\w+)*?)(?:\s+for\s+|\s+)(\d+(?:\.\d+)?)'
    matches1 = re.findall(pattern1, text)
    
    for match in matches1:
        expense_name = match[0].strip()
        amount = float(match[1])
        
        # Skip if it's just a number or common words
        if expense_name and not expense_name.isdigit() and expense_name not in ['for', 'and', 'paid', 'bought', 'spent']:
            expenses.append({
                "expense": expense_name,
                "amount": amount
            })
    
    # Pattern 2: "amount on item" 
    # Matches: "200 on coffee", "150 on snacks"
    pattern2 = r'(\d+(?:\.\d+)?)\s+on\s+(\w+(?:\s+\w+)*?)'
    matches2 = re.findall(pattern2, text)
    
    for match in matches2:
        amount = float(match[0])
        expense_name = match[1].strip()
        
        if expense_name and not expense_name.isdigit():
            expenses.append({
                "expense": expense_name,
                "amount": amount
            })
    
    # If no patterns matched, try a more flexible approach
    if not expenses:
        expenses = _fallback_parsing(text)
    
    return expenses

def _fallback_parsing(text: str) -> List[Dict[str, Any]]:
    """
    Fallback parsing for cases where main patterns don't match.
    Uses more flexible regex to find number-word pairs.
    """
    expenses = []
    
    # Find all numbers and nearby words
    # Pattern: word(s) followed by number, or number followed by word(s)
    patterns = [
        r'(\w+(?:\s+\w+)*?)\s+(\d+(?:\.\d+)?)',  # word(s) number
        r'(\d+(?:\.\d+)?)\s+(\w+(?:\s+\w+)*?)',  # number word(s)
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            # Determine which is the expense and which is the amount
            if match[0].replace('.', '').isdigit():
                amount = float(match[0])
                expense_name = match[1].strip()
            else:
                expense_name = match[0].strip()
                amount = float(match[1])
            
            # Filter out common words and ensure valid expense name
            skip_words = {'for', 'and', 'paid', 'bought', 'spent', 'on', 'the', 'a', 'an'}
            if (expense_name.lower() not in skip_words and 
                len(expense_name) > 1 and 
                not expense_name.isdigit()):
                
                expenses.append({
                    "expense": expense_name,
                    "amount": amount
                })
    
    return expenses

def enhance_expense_names(expenses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Enhance expense names with better formatting and common aliases.
    """
    # Common aliases and corrections
    aliases = {
        'transport': ['bus', 'taxi', 'uber', 'okada', 'keke'],
        'airtime': ['recharge', 'credit', 'phone credit'],
        'food': ['lunch', 'dinner', 'breakfast', 'meal', 'eating'],
        'snacks': ['biscuit', 'drink', 'soda', 'water'],
        'fuel': ['petrol', 'gas', 'diesel'],
        'internet': ['data', 'wifi', 'subscription'],
    }
    
    enhanced_expenses = []
    for expense in expenses:
        expense_name = expense['expense'].lower()
        
        # Check for aliases
        for main_name, alias_list in aliases.items():
            if expense_name in alias_list:
                expense['expense'] = main_name
                break
        else:
            # Capitalize first letter if no alias found
            expense['expense'] = expense_name.capitalize()
        
        enhanced_expenses.append(expense)
    
    return enhanced_expenses

def parse_and_enhance(input_text: str) -> List[Dict[str, Any]]:
    """
    Complete parsing pipeline: parse natural language and enhance names.
    """
    expenses = parse_natural_expenses(input_text)
    return enhance_expense_names(expenses)

# Test examples
if __name__ == "__main__":
    test_inputs = [
        "Bought airtime for 500 and lunch for 1500",
        "Paid transport 800, airtime 300",
        "Spent ₦200 on coffee and ₦150 on snacks",
        "Food 1200, transport 500, airtime 300",
        "Bus fare 200, recharge 500, lunch 800",
        "500 for fuel and 300 for water"
    ]
    
    for test_input in test_inputs:
        print(f"\nInput: {test_input}")
        result = parse_and_enhance(test_input)
        print(f"Parsed: {result}")