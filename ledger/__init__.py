"""
Legacy ledger package.

This package is deprecated. Please use the new structure:
- Core logic: src.ledger.services
- API: src.api
- CLI: src.cli

This file is kept for backward compatibility during migration.
"""

# Re-export from new structure for backward compatibility
try:
    from src.ledger.services import (
        ExpenseService,
        CategoryService,
        BudgetService,
        AnalyticsService,
        UserService,
    )
    from src.ledger.config import get_settings
    from src.ledger.parsers.nlp_parser import parse_and_enhance
    
    __all__ = [
        "ExpenseService",
        "CategoryService", 
        "BudgetService",
        "AnalyticsService",
        "UserService",
        "get_settings",
        "parse_and_enhance",
    ]
except ImportError:
    # If new structure not available, provide empty exports
    __all__ = []

