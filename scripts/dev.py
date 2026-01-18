#!/usr/bin/env python3.13
"""
QuickLedger Development Server Runner
A Python script to run both API and frontend servers simultaneously
"""

import os
import sys
import time
import signal
import subprocess
import threading
from pathlib import Path

class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'  # No Color

class DevServer:
    def __init__(self):
        self.api_process = None
        self.frontend_process = None
        self.running = True
        
    def print_status(self, message, color=Colors.BLUE):
        print(f"{color}[QuickLedger]{Colors.NC} {message}")
        
    def print_success(self, message):
        self.print_status(message, Colors.GREEN)
        
    def print_error(self, message):
        self.print_status(message, Colors.RED)
        
    def print_warning(self, message):
        self.print_status(message, Colors.YELLOW)
    
    def check_dependencies(self):
        """Check if required dependencies are installed"""
        try:
            import fastapi
            import uvicorn
            self.print_success("✅ Python dependencies found")
            return True
        except ImportError:
            self.print_warning("⚠️  Installing Python dependencies...")
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                             check=True, capture_output=True)
                self.print_success("✅ Dependencies installed successfully")
                return True
            except subprocess.CalledProcessError as e:
                self.print_error(f"❌ Failed to install dependencies: {e}")
                return False
    
    def start_api_server(self):
        """Start the FastAPI server"""
        try:
            self.print_status("🔧 Starting API server on http://localhost:8000")
            
            # Change to src/api directory
            api_dir = Path("src/api")
            if not api_dir.exists():
                self.print_error("❌ API directory not found")
                return False
                
            self.api_process = subprocess.Popen([
                sys.executable, "-m", "uvicorn", "main:app", 
                "--reload", "--host", "0.0.0.0", "--port", "8000"
            ], cwd=api_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            return True
        except Exception as e:
            self.print_error(f"❌ Failed to start API server: {e}")
            return False
    
    def start_frontend_server(self):
        """Start the frontend server"""
        try:
            self.print_status("🌐 Starting frontend server on http://localhost:3000")
            
            # Change to frontend directory
            frontend_dir = Path("frontend")
            if not frontend_dir.exists():
                self.print_error("❌ Frontend directory not found")
                return False
                
            self.frontend_process = subprocess.Popen([
                sys.executable, "-m", "http.server", "3000"
            ], cwd=frontend_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            return True
        except Exception as e:
            self.print_error(f"❌ Failed to start frontend server: {e}")
            return False
    
    def monitor_processes(self):
        """Monitor both processes and restart if needed"""
        while self.running:
            time.sleep(2)
            
            # Check API process
            if self.api_process and self.api_process.poll() is not None:
                self.print_error("❌ API server stopped unexpectedly")
                break
                
            # Check frontend process
            if self.frontend_process and self.frontend_process.poll() is not None:
                self.print_error("❌ Frontend server stopped unexpectedly")
                break
    
    def cleanup(self):
        """Clean up processes"""
        self.running = False
        self.print_status("🛑 Shutting down servers...")
        
        if self.api_process:
            self.api_process.terminate()
            try:
                self.api_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.api_process.kill()
                
        if self.frontend_process:
            self.frontend_process.terminate()
            try:
                self.frontend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.frontend_process.kill()
                
        self.print_success("✅ Servers stopped successfully!")
    
    def signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully"""
        print()  # New line after ^C
        self.cleanup()
        sys.exit(0)
    
    def run(self):
        """Main run method"""
        # Set up signal handler
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        self.print_status("🚀 Starting QuickLedger development environment...")
        
        # Check dependencies
        if not self.check_dependencies():
            return 1
        
        # Start servers
        if not self.start_api_server():
            return 1
            
        # Give API time to start
        time.sleep(3)
        
        if not self.start_frontend_server():
            self.cleanup()
            return 1
        
        # Give frontend time to start
        time.sleep(2)
        
        # Print success message
        self.print_success("✅ Both servers are running!")
        self.print_success("🌐 Frontend: http://localhost:3000")
        self.print_success("🔧 API: http://localhost:8000")
        self.print_success("📚 API Docs: http://localhost:8000/docs")
        self.print_status("Press Ctrl+C to stop both servers")
        
        # Start monitoring in a separate thread
        monitor_thread = threading.Thread(target=self.monitor_processes)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        # Keep main thread alive
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        
        self.cleanup()
        return 0

if __name__ == "__main__":
    # Change to project root directory
    script_dir = Path(__file__).parent.parent
    os.chdir(script_dir)
    
    server = DevServer()
    sys.exit(server.run())