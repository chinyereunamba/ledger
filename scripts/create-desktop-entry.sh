#!/bin/bash

# Simple QuickLedger Desktop Entry Creator
# Creates just the desktop entry without installing dependencies

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[Desktop Entry]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[Desktop Entry]${NC} $1"
}

print_error() {
    echo -e "${RED}[Desktop Entry]${NC} $1"
}

# Get the absolute path of the current directory
CURRENT_DIR=$(pwd)
DESKTOP_FILE="$HOME/.local/share/applications/quickledger.desktop"
ICON_DIR="$HOME/.local/share/icons/hicolor/192x192/apps"

print_status "📝 Creating QuickLedger desktop entry..."

# Check if launcher script exists
if [ ! -f "quickledger-launcher.py" ]; then
    print_error "❌ quickledger-launcher.py not found in current directory"
    print_error "Please run this script from the QuickLedger project directory"
    exit 1
fi

# Create directories
mkdir -p "$HOME/.local/share/applications"
mkdir -p "$ICON_DIR"

# Copy icon if it exists
if [ -f "frontend/icons/icon-192x192.png" ]; then
    cp "frontend/icons/icon-192x192.png" "$ICON_DIR/quickledger.png"
    print_success "✅ Icon installed"
else
    print_status "⚠️  Icon not found, using default"
fi

# Create desktop entry
print_status "📄 Creating desktop entry at: $DESKTOP_FILE"
cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=QuickLedger
Comment=Smart Expense Tracker PWA
Exec=python3.13 "$CURRENT_DIR/quickledger-launcher.py"
Icon=quickledger
Path=$CURRENT_DIR
Terminal=false
StartupNotify=true
Categories=Office;Finance;Utility;
Keywords=expense;tracker;finance;budget;money;pwa;
StartupWMClass=QuickLedger
EOF

# Make desktop file executable
chmod +x "$DESKTOP_FILE"

# Verify the desktop file was created
if [ -f "$DESKTOP_FILE" ]; then
    print_success "✅ Desktop entry created successfully"
    print_status "📄 Location: $DESKTOP_FILE"
else
    print_error "❌ Failed to create desktop entry"
    exit 1
fi

# Update desktop database
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true
    print_success "✅ Desktop database updated"
fi

print_success "🎯 QuickLedger should now appear in your applications menu"

# Ask if user wants to create a desktop shortcut
read -p "$(echo -e "${BLUE}[Desktop Entry]${NC} Create desktop shortcut? (y/n): ")" -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    DESKTOP_SHORTCUT="$HOME/Desktop/QuickLedger.desktop"
    cp "$DESKTOP_FILE" "$DESKTOP_SHORTCUT"
    chmod +x "$DESKTOP_SHORTCUT"
    
    # Mark as trusted (for some desktop environments)
    if command -v gio &> /dev/null; then
        gio set "$DESKTOP_SHORTCUT" metadata::trusted true 2>/dev/null || true
    fi
    
    print_success "✅ Desktop shortcut created at: $DESKTOP_SHORTCUT"
fi

print_success "🎉 Desktop entry creation complete!"