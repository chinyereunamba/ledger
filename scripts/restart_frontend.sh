#!/bin/bash

# Get script directory (project root)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$SCRIPT_DIR"

echo "🔄 Restarting QuickLedger Frontend..."

# Kill existing frontend server
echo "Stopping existing frontend server..."
pkill -f "python3 -m http.server 3000" || echo "No existing server found"

# Wait a moment
sleep 2

# Start fresh frontend server
echo "Starting fresh frontend server on port 3000..."
cd "$SCRIPT_DIR/frontend" && python3 -m http.server 3000 &

# Get the PID
FRONTEND_PID=$!
echo "✅ Frontend server started with PID: $FRONTEND_PID"

# Wait a moment for server to start
sleep 3

# Check if server is running
if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Frontend server is running successfully!"
    echo "🌐 Open: http://localhost:3000"
    echo ""
    echo "🎯 Changes Applied:"
    echo "   - Case-insensitive category consolidation"
    echo "   - Consistent expense name formatting"
    echo "   - Category display in expense lists"
    echo "   - Enhanced charts and analytics"
    echo ""
    echo "💡 If you still don't see changes, try:"
    echo "   - Hard refresh: Ctrl+F5 (Windows/Linux) or Cmd+Shift+R (Mac)"
    echo "   - Open in incognito/private mode"
    echo "   - Clear browser cache"
else
    echo "❌ Frontend server failed to start"
    exit 1
fi