#!/bin/bash

# QuickLedger Development Server Runner
# This script starts both the API and frontend servers

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[QuickLedger]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[QuickLedger]${NC} $1"
}

print_error() {
    echo -e "${RED}[QuickLedger]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[QuickLedger]${NC} $1"
}

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Function to kill processes on specific ports
cleanup_ports() {
    print_status "Cleaning up ports 8000 and 3000..."
    
    if check_port 8000; then
        print_warning "Port 8000 is in use, attempting to free it..."
        pkill -f "uvicorn.*8000" 2>/dev/null || true
        sleep 1
    fi
    
    if check_port 3000; then
        print_warning "Port 3000 is in use, attempting to free it..."
        pkill -f "python.*http.server.*3000" 2>/dev/null || true
        sleep 1
    fi
}

# Function to start the API server
start_api() {
    print_status "Starting FastAPI server on http://localhost:8000"
    cd "$SCRIPT_DIR/src/api"
    uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
    API_PID=$!
    cd "$SCRIPT_DIR"
    echo $API_PID > .api_pid
}

# Function to start the frontend server
start_frontend() {
    print_status "Starting frontend server on http://localhost:3000"
    cd "$SCRIPT_DIR/frontend"
    python3.13 -m http.server 3000 &
    FRONTEND_PID=$!
    cd "$SCRIPT_DIR"
    echo $FRONTEND_PID > .frontend_pid
}

# Function to cleanup on exit
cleanup() {
    print_status "Shutting down servers..."
    
    if [ -f .api_pid ]; then
        API_PID=$(cat .api_pid)
        kill $API_PID 2>/dev/null || true
        rm -f .api_pid
    fi
    
    if [ -f .frontend_pid ]; then
        FRONTEND_PID=$(cat .frontend_pid)
        kill $FRONTEND_PID 2>/dev/null || true
        rm -f .frontend_pid
    fi
    
    cleanup_ports
    print_success "Servers stopped successfully!"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Get script directory (project root)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$SCRIPT_DIR"

# Main execution
print_status "🚀 Starting QuickLedger development environment..."

# Check if Python dependencies are installed
if [ ! -d ".venv" ] && ! python3.13 -c "import fastapi" 2>/dev/null; then
    print_warning "FastAPI not found. Installing dependencies..."
    python3.13 -m pip install -r requirements.txt
fi

# Clean up any existing processes
cleanup_ports

# Start servers
start_api
sleep 2  # Give API time to start

start_frontend
sleep 1

# Check if servers started successfully
if check_port 8000 && check_port 3000; then
    print_success "✅ Both servers are running!"
    print_success "🌐 Frontend: http://localhost:3000"
    print_success "🔧 API: http://localhost:8000"
    print_success "📚 API Docs: http://localhost:8000/docs"
    print_status "Press Ctrl+C to stop both servers"
    
    # Wait for user to stop
    wait
else
    print_error "❌ Failed to start servers. Check the logs above."
    cleanup
    exit 1
fi