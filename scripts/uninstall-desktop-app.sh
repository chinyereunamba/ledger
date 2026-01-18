#!/bin/bash

# QuickLedger Desktop App Uninstaller
# This script removes QuickLedger desktop application

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[QuickLedger Uninstaller]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[QuickLedger Uninstaller]${NC} $1"
}

print_error() {
    echo -e "${RED}[QuickLedger Uninstaller]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[QuickLedger Uninstaller]${NC} $1"
}

DESKTOP_FILE="$HOME/.local/share/applications/quickledger.desktop"
ICON_FILE="$HOME/.local/share/icons/hicolor/192x192/apps/quickledger.png"
DESKTOP_SHORTCUT="$HOME/Desktop/QuickLedger.desktop"

print_status "🗑️  Uninstalling QuickLedger desktop application..."

# Remove desktop entry
if [ -f "$DESKTOP_FILE" ]; then
    rm "$DESKTOP_FILE"
    print_success "✅ Desktop entry removed"
else
    print_warning "⚠️  Desktop entry not found"
fi

# Remove icon
if [ -f "$ICON_FILE" ]; then
    rm "$ICON_FILE"
    print_success "✅ Icon removed"
else
    print_warning "⚠️  Icon not found"
fi

# Remove desktop shortcut
if [ -f "$DESKTOP_SHORTCUT" ]; then
    rm "$DESKTOP_SHORTCUT"
    print_success "✅ Desktop shortcut removed"
else
    print_warning "⚠️  Desktop shortcut not found"
fi

# Update desktop database
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$HOME/.local/share/applications"
    print_success "✅ Desktop database updated"
fi

print_success "🎉 QuickLedger desktop application uninstalled successfully!"
print_status "📝 Note: Python dependencies and project files remain intact"
print_status "💡 To remove Python dependencies, run: python3.13 -m pip uninstall -r requirements.txt"