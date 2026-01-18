#!/bin/bash

# QuickLedger Desktop App Installer
# This script installs QuickLedger as a desktop application

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[QuickLedger Installer]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[QuickLedger Installer]${NC} $1"
}

print_error() {
    echo -e "${RED}[QuickLedger Installer]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[QuickLedger Installer]${NC} $1"
}

# Get the absolute path of the current directory
CURRENT_DIR=$(pwd)
DESKTOP_FILE="$HOME/.local/share/applications/quickledger.desktop"
ICON_DIR="$HOME/.local/share/icons/hicolor/192x192/apps"

print_status "🚀 Installing QuickLedger as a desktop application..."

# Check if launcher script exists
if [ ! -f "quickledger-launcher.py" ]; then
    print_error "❌ quickledger-launcher.py not found in current directory"
    print_error "Please run this script from the QuickLedger project directory"
    exit 1
fi

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    print_error "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Check if tkinter is available
if ! python3 -c "import tkinter" 2>/dev/null; then
    print_warning "⚠️  tkinter not found. Installing python3-tk..."
    
    # Try different package managers
    if command -v apt &> /dev/null; then
        sudo apt update && sudo apt install -y python3-tk
    elif command -v yum &> /dev/null; then
        sudo yum install -y tkinter
    elif command -v dnf &> /dev/null; then
        sudo dnf install -y python3-tkinter
    elif command -v pacman &> /dev/null; then
        sudo pacman -S tk
    else
        print_error "❌ Could not install tkinter. Please install python3-tk manually."
        exit 1
    fi
fi

# Install Python dependencies
print_status "📦 Installing Python dependencies..."
python3 -m pip install -r requirements.txt --user

# Create directories
mkdir -p "$HOME/.local/share/applications"
mkdir -p "$ICON_DIR"

# Copy icon if it exists
if [ -f "frontend/icons/icon-192x192.png" ]; then
    cp "frontend/icons/icon-192x192.png" "$ICON_DIR/quickledger.png"
    print_success "✅ Icon installed"
fi

# Create desktop entry with absolute paths
print_status "📝 Creating desktop entry at: $DESKTOP_FILE"
cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=QuickLedger
Comment=Smart Expense Tracker PWA
Exec=python3 "$CURRENT_DIR/quickledger-launcher.py"
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
    print_status "📄 Desktop file location: $DESKTOP_FILE"
else
    print_error "❌ Failed to create desktop entry"
    exit 1
fi

# Update desktop database
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$HOME/.local/share/applications"
fi

print_success "✅ QuickLedger desktop application installed successfully!"
print_success "🎯 You can now find 'QuickLedger' in your applications menu"
print_success "📱 Or run it directly with: python3 quickledger-launcher.py"

# Ask if user wants to create a desktop shortcut
read -p "$(echo -e "${BLUE}[QuickLedger Installer]${NC} Create desktop shortcut? (y/n): ")" -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    DESKTOP_SHORTCUT="$HOME/Desktop/QuickLedger.desktop"
    cp "$DESKTOP_FILE" "$DESKTOP_SHORTCUT"
    chmod +x "$DESKTOP_SHORTCUT"
    
    # Mark as trusted (for some desktop environments)
    if command -v gio &> /dev/null; then
        gio set "$DESKTOP_SHORTCUT" metadata::trusted true
    fi
    
    print_success "✅ Desktop shortcut created!"
fi

print_success "🎉 Installation complete! Enjoy using QuickLedger!"