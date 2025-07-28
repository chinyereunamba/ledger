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
    - "I spent 300 on fish"
    """
    expenses = []
    
    # Clean and normalize input
    text = input_text.lower().strip()
    
    # Remove common currency symbols and normalize
    text = re.sub(r'[₦$£€]', '', text)
    
    # Pattern 1: "amount on item" (highest priority)
    # Matches: "300 on fish", "200 on coffee", "150 on snacks"
    pattern_on = r'(\d+(?:\.\d+)?)\s+on\s+(\w+(?:\s+\w+)*?)(?=\s+and\s+|\s*,|\s*$)'
    matches_on = re.findall(pattern_on, text)
    
    for match in matches_on:
        amount = float(match[0])
        expense_name = match[1].strip()
        
        if _is_valid_expense_name(expense_name):
            expenses.append({
                "expense": expense_name,
                "amount": amount
            })
    
    # Pattern 2: "item for amount" 
    # Matches: "airtime for 500", "lunch for 1500"
    if not expenses:  
        pattern_for = r'(\w+(?:\s+\w+)*?)\s+for\s+(\d+(?:\.\d+)?)(?=\s+and\s+|\s*,|\s*$)'
        matches_for = re.findall(pattern_for, text)
        
        for match in matches_for:
            expense_name = match[0].strip()
            amount = float(match[1])
            
            if _is_valid_expense_name(expense_name):
                expenses.append({
                    "expense": expense_name,
                    "amount": amount
                })
    
    # Pattern 3: Comma-separated "item amount" pairs
    # Split by commas and "and" first, then parse each part
    if not expenses:
        
        parts = re.split(r'\s*,\s*|\s+and\s+', text)
        
        for part in parts:
            part = part.strip()
            if not part:
                continue
                
            # Look for "item amount" in each part
            match = re.search(r'(\w+(?:\s+\w+)*?)\s+(\d+(?:\.\d+)?)$', part)
            if match:
                expense_name = match.group(1).strip()
                amount = float(match.group(2))
                
                if _is_valid_expense_name(expense_name):
                    expenses.append({
                        "expense": expense_name,
                        "amount": amount
                    })
    
    # If still no patterns matched, try fallback parsing
    if not expenses:
        expenses = _fallback_parsing(text)
    
    return expenses

def _is_valid_expense_name(name: str) -> bool:
    """
    Check if a name is a valid expense name (not a common phrase or stop word).
    """
    name = name.lower().strip()
    
    # Skip empty or numeric names
    if not name or name.isdigit():
        return False
    
    # Common phrases and stop words to ignore
    stop_phrases = {
        'i', 'i spent', 'spent', 'paid', 'bought', 'purchase', 'purchased',
        'for', 'and', 'the', 'a', 'an', 'on', 'with', 'to', 'from',
        'my', 'me', 'we', 'us', 'our', 'this', 'that', 'these', 'those',
        'was', 'were', 'is', 'are', 'am', 'be', 'been', 'being',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'could', 'should', 'may', 'might', 'can', 'must', 'shall'
    }
    
    # Check if the entire name is a stop phrase
    if name in stop_phrases:
        return False
    
    # Check if it starts with common stop phrases
    for phrase in ['i spent', 'i paid', 'i bought', 'we spent', 'we paid']:
        if name.startswith(phrase):
            return False
    
    # Must be at least 2 characters and contain at least one letter
    if len(name) < 2 or not any(c.isalpha() for c in name):
        return False
    
    return True

def _fallback_parsing(text: str) -> List[Dict[str, Any]]:
    """
    Fallback parsing for cases where main patterns don't match.
    Uses more flexible regex to find number-word pairs.
    """
    expenses = []
    
    # Find all numbers and nearby words
    # Pattern: word(s) followed by number, or number followed by word(s)
    patterns = [
        r'(\w+(?:\s+\w+)*?)\s+(\d+(?:\.\d+)?)', 
        r'(\d+(?:\.\d+)?)\s+(\w+(?:\s+\w+)*?)',  
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
            
            # Use the same validation function
            if _is_valid_expense_name(expense_name):
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
        "I spent 300 on fish",  
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
        if test_input == "I spent 300 on fish":
            if len(result) == 1 and result[0]['expense'].lower() == 'fish':
                print("✅ FISH TEST PASSED")
            else:
                print("❌ FISH TEST FAILED")