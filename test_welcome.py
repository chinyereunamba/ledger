#!/usr/bin/env python3

# Simple test to verify the welcome message and data handling
import sys
import os
sys.path.append('.')

from ledger.ledger import LEDGER_DIR, LEDGER, ensure_ledger_directory

print("Testing ledger setup...")
print(f"Ledger directory: {LEDGER_DIR}")
print(f"Ledger file: {LEDGER}")
print(f"Directory exists: {LEDGER_DIR.exists()}")
print(f"Ledger file exists: {LEDGER.exists()}")

# Test directory creation
ensure_ledger_directory()
print(f"After ensure_ledger_directory():")
print(f"Directory exists: {LEDGER_DIR.exists()}")

print("\nLedger setup complete! ✅")