#!/usr/bin/env python3
"""
QuickLedger CLI Launcher
A command-line launcher that starts the servers and opens the PWA
"""

import os
import sys
import time
import subprocess
import webbrowser
from pathlib import Path
import signal
import atexit

class QuickLedgerCLILauncher:
    def __init__(self):
        self.api_process = None
        self.frontend_process = None
        self.servers_running = False
        
        # Register cleanup function
        atexit.register(self.cleanup)
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
    def print_status(self, message, color_code="0"):
        """Print colored status message"""
        colors = {
            "0": "",  # default
            "32": "\033[32m",  # green
            "33": "\033[33m",  # yellow
            "31": "\033[31m",  # red
            "34": "\033[34m",  # blue
        }
        reset = "\033[0m" if color_code != "0" else ""
        print(f"{colors.get(color_code, '')}{message}{reset}")
        
    def check_dependencies(self):
        """Check if required dependencies are installed"""
        try:
            import fastapi
            import uvicorn
            return True
        except ImportError:
            self.print_status("Installing dependencies...", "33")
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                             check=True, capture_output=True)
                return True
            except subprocess.CalledProcessError as e:
                self.print_status(f"Failed to install dependencies: {e}", "31")
                return False
    
    def start_servers(self):
        """Start both API and frontend servers"""
        try:
            # Check dependencies
            if not self.check_dependencies():
                self.print_status("❌ Failed to install dependencies", "31")
                return False
            
            self.print_status("🔧 Starting API server...", "34")
            
            # Start API server
            api_dir = Path("src/api").resolve()
            if not api_dir.exists():
                self.print_status("❌ API directory not found", "31")
                return False
            
            # Get current working directory and set up environment
            current_dir = Path.cwd()
            env = os.environ.copy()
            env['PYTHONPATH'] = str(current_dir)
            
            # Start API server
            self.api_process = subprocess.Popen([
                sys.executable, "-m", "uvicorn", "main:app", 
                "--reload", "--host", "0.0.0.0", "--port", "8000"
            ], cwd=str(api_dir), env=env, 
               stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
               universal_newlines=True, bufsize=1)
            
            # Check if API started successfully
            time.sleep(3)
            if self.api_process.poll() is not None:
                # Process died, get the error output
                output, _ = self.api_process.communicate()
                self.print_status(f"❌ API failed to start: {output[:200]}...", "31")
                return False
            
            self.print_status("🌐 Starting frontend server...", "34")
            
            # Start frontend server
            frontend_dir = Path("frontend").resolve()
            if not frontend_dir.exists():
                self.print_status("❌ Frontend directory not found", "31")
                return False
                
            self.frontend_process = subprocess.Popen([
                sys.executable, "-m", "http.server", "3000"
            ], cwd=str(frontend_dir), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait a bit for frontend to start
            time.sleep(2)
            
            # Verify both processes are still running
            if self.api_process.poll() is not None:
                self.print_status("❌ API server stopped unexpectedly", "31")
                return False
                
            if self.frontend_process.poll() is not None:
                self.print_status("❌ Frontend server stopped unexpectedly", "31")
                return False
            
            self.servers_running = True
            return True
            
        except Exception as e:
            self.print_status(f"❌ Error: {str(e)}", "31")
            return False
    
    def stop_servers(self):
        """Stop both servers"""
        self.print_status("🛑 Stopping servers...", "33")
        
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
        
        self.servers_running = False
        self.print_status("✅ Servers stopped", "32")
    
    def cleanup(self):
        """Cleanup function called on exit"""
        if self.servers_running:
            self.stop_servers()
    
    def signal_handler(self, signum, frame):
        """Handle interrupt signals"""
        self.print_status("\n🛑 Received interrupt signal, stopping servers...", "33")
        self.cleanup()
        sys.exit(0)
    
    def run(self):
        """Run the application"""
        print("💰 QuickLedger - Smart Expense Tracker")
        print("=" * 40)
        
        if self.start_servers():
            self.print_status("✅ Servers running successfully!", "32")
            self.print_status("📱 Opening QuickLedger in your browser...", "34")
            
            # Auto-open the PWA
            time.sleep(1)
            webbrowser.open("http://localhost:3000")
            
            self.print_status("\n🔗 Quick Links:", "34")
            self.print_status("   📱 App: http://localhost:3000")
            self.print_status("   🔧 API Docs: http://localhost:8000/docs")
            self.print_status("\n💡 Press Ctrl+C to stop the servers and exit")
            
            # Keep the script running
            try:
                while self.servers_running:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
        else:
            self.print_status("❌ Failed to start servers", "31")
            return False

if __name__ == "__main__":
    # Change to project root directory
    script_dir = Path(__file__).parent.parent
    os.chdir(script_dir)
    
    app = QuickLedgerCLILauncher()
    app.run()