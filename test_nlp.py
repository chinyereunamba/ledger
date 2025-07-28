#!/usr/bin/env python3
"""
Test the NLP parsing functionality
"""

from ledger.nlp_parser import parse_and_enhance

def test_nlp_parsing():
    """Test various natural language inputs"""
    
    test_cases = [
        {
            "input": "Bought airtime for 500 and lunch for 1500",
            "expected_count": 2
        },
        {
            "input": "Paid transport 800, airtime 300",
            "expected_count": 2
        },
        {
            "input": "Spent ₦200 on coffee and ₦150 on snacks",
            "expected_count": 2
        },
        {
            "input": "Food 1200, transport 500, airtime 300",
            "expected_count": 3
        },
        {
            "input": "Bus fare 200, recharge 500, lunch 800",
            "expected_count": 3
        },
        {
            "input": "500 for fuel and 300 for water",
            "expected_count": 2
        },
        {
            "input": "Coffee 50",
            "expected_count": 1
        }
    ]
    
    print("🧪 Testing NLP Expense Parsing")
    print("=" * 50)
    
    all_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        input_text = test_case["input"]
        expected_count = test_case["expected_count"]
        
        print(f"\n{i}. Input: \"{input_text}\"")
        
        try:
            result = parse_and_enhance(input_text)
            actual_count = len(result)
            
            print(f"   Parsed: {result}")
            print(f"   Expected {expected_count} expenses, got {actual_count}")
            
            if actual_count == expected_count:
                print("   ✅ PASS")
            else:
                print("   ❌ FAIL")
                all_passed = False
                
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All NLP tests passed!")
    else:
        print("❌ Some NLP tests failed.")
    
    return all_passed

def test_enhancement():
    """Test expense name enhancement (aliases)"""
    print("\n🔧 Testing Expense Name Enhancement")
    print("-" * 30)
    
    test_cases = [
        {"input": "bus 200", "expected_expense": "transport"},
        {"input": "recharge 500", "expected_expense": "airtime"},
        {"input": "lunch 800", "expected_expense": "food"},
        {"input": "petrol 1000", "expected_expense": "fuel"},
    ]
    
    for test_case in test_cases:
        result = parse_and_enhance(test_case["input"])
        if result:
            actual_expense = result[0]["expense"]
            expected_expense = test_case["expected_expense"]
            
            print(f"Input: '{test_case['input']}' -> '{actual_expense}'", end="")
            if actual_expense == expected_expense:
                print(" ✅")
            else:
                print(f" ❌ (expected '{expected_expense}')")

if __name__ == "__main__":
    test_nlp_parsing()
    test_enhancement()
    
    print("\n💡 Try the CLI command:")
    print("  python main.py say \"Bought airtime for 500 and lunch for 1500\"")
    
    print("\n🌐 Or test the API:")
    print("  curl -X POST http://localhost:8000/nlp/parse \\")
    print("    -H 'Content-Type: application/json' \\")
    print("    -d '{\"text\": \"Bought airtime for 500 and lunch for 1500\"}'")