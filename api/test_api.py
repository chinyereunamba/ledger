#!/usr/bin/env python3
"""
Simple test to verify the modular API structure works
"""

def test_imports():
    """Test that all modules can be imported successfully"""
    try:
        print("Testing imports...")
        
        # Test models
        from models import ExpenseCreate, ExpenseUpdate, ExpenseResponse
        print("✅ Models imported successfully")
        
        # Test utils
        from utils import load_ledger_data, validate_date_format
        print("✅ Utils imported successfully")
        
        # Test routes
        from routes.expenses import router as expenses_router
        from routes.analytics import router as analytics_router
        from routes.utility import router as utility_router
        print("✅ Routes imported successfully")
        
        # Test main app
        from main import app
        print("✅ Main app imported successfully")
        
        print("\n🎉 All imports successful! The modular structure is working.")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_app_structure():
    """Test that the FastAPI app has the expected structure"""
    try:
        from main import app
        
        # Check that routes are included
        routes = [route.path for route in app.routes]
        
        expected_routes = [
            "/expenses",
            "/expenses/{date}/{index}",
            "/summary",
            "/stats",
            "/health",
            "/"
        ]
        
        print("\nTesting app structure...")
        print(f"Found {len(routes)} routes:")
        for route in routes:
            print(f"  - {route}")
        
        # Check if expected routes exist
        missing_routes = []
        for expected in expected_routes:
            # Simple check - just see if the base path exists
            base_path = expected.split("{")[0].rstrip("/")
            if not any(base_path in route for route in routes):
                missing_routes.append(expected)
        
        if missing_routes:
            print(f"❌ Missing routes: {missing_routes}")
            return False
        else:
            print("✅ All expected routes found")
            return True
            
    except Exception as e:
        print(f"❌ Error testing app structure: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Modular API Structure")
    print("=" * 40)
    
    success = True
    success &= test_imports()
    success &= test_app_structure()
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 All tests passed! API is ready to run.")
        print("\nTo start the server:")
        print("  fastapi dev main.py")
        print("\nAlternatives:")
        print("  python run.py")
        print("  uvicorn main:app --reload")
    else:
        print("❌ Some tests failed. Check the errors above.")