#!/usr/bin/env python3.13
"""
QuickLedger Desktop Launcher
A GUI application launcher that starts the servers and opens the PWA
"""

import os
import sys
import time
import subprocess
import threading
import webbrowser
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
import signal

class QuickLedgerLauncher:
    def __init__(self):
        self.root = tk.Tk()
        self.api_process = None
        self.frontend_process = None
        self.servers_running = False
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the GUI"""
        self.root.title("QuickLedger - Smart Expense Tracker")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        
        # Set icon if available
        try:
            icon_path = Path("frontend/icons/icon-192x192.png")
            if icon_path.exists():
                self.root.iconphoto(True, tk.PhotoImage(file=str(icon_path)))
        except:
            pass
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="💰 QuickLedger", 
                               font=("Arial", 18, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        subtitle_label = ttk.Label(main_frame, text="Smart Expense Tracker PWA", 
                                  font=("Arial", 10))
        subtitle_label.grid(row=1, column=0, columnspan=2, pady=(0, 20))
        
        # Status
        self.status_label = ttk.Label(main_frame, text="Ready to start", 
                                     font=("Arial", 10))
        self.status_label.grid(row=2, column=0, columnspan=2, pady=(0, 10))
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=4, column=0, columnspan=2, pady=(0, 10))
        
        # Start button
        self.start_button = ttk.Button(buttons_frame, text="🚀 Start QuickLedger", 
                                      command=self.start_application, width=20)
        self.start_button.grid(row=0, column=0, padx=(0, 10))
        
        # Stop button
        self.stop_button = ttk.Button(buttons_frame, text="🛑 Stop Servers", 
                                     command=self.stop_servers, width=15, state='disabled')
        self.stop_button.grid(row=0, column=1)
        
        # Links frame
        links_frame = ttk.Frame(main_frame)
        links_frame.grid(row=5, column=0, columnspan=2, pady=(20, 0))
        
        # Quick access buttons
        ttk.Button(links_frame, text="📱 Open App", 
                  command=lambda: webbrowser.open("http://localhost:3000"), 
                  width=12).grid(row=0, column=0, padx=(0, 5))
        
        ttk.Button(links_frame, text="🔧 API Docs", 
                  command=lambda: webbrowser.open("http://localhost:8000/docs"), 
                  width=12).grid(row=0, column=1, padx=5)
        
        ttk.Button(links_frame, text="🐛 Debug", 
                  command=self.debug_api_startup, 
                  width=12).grid(row=0, column=2, padx=5)
        
        ttk.Button(links_frame, text="❌ Exit", 
                  command=self.on_closing, 
                  width=12).grid(row=0, column=3, padx=(5, 0))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # Handle window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def update_status(self, message, color="black"):
        """Update status label"""
        self.status_label.config(text=message, foreground=color)
        self.root.update()
        
    def start_progress(self):
        """Start progress bar animation"""
        self.progress.start(10)
        
    def stop_progress(self):
        """Stop progress bar animation"""
        self.progress.stop()
        
    def check_dependencies(self):
        """Check if required dependencies are installed"""
        try:
            import fastapi
            import uvicorn
            return True
        except ImportError:
            self.update_status("Installing dependencies...", "orange")
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                             check=True, capture_output=True)
                return True
            except subprocess.CalledProcessError:
                return False
    
    def debug_api_startup(self):
        """Debug method to test API startup manually"""
        try:
            api_dir = Path("src/api").resolve()
            current_dir = Path.cwd()
            env = os.environ.copy()
            env['PYTHONPATH'] = str(current_dir)
            
            print(f"API Directory: {api_dir}")
            print(f"Current Directory: {current_dir}")
            print(f"Python Path: {env.get('PYTHONPATH', 'Not set')}")
            print(f"API directory exists: {api_dir.exists()}")
            
            # Test if main.py exists
            main_py = api_dir / "main.py"
            print(f"main.py exists: {main_py.exists()}")
            
            # Test the actual startup command with a timeout
            print("Testing actual API startup...")
            process = subprocess.Popen([
                sys.executable, "-m", "uvicorn", "main:app", 
                "--host", "0.0.0.0", "--port", "8000"
            ], cwd=str(api_dir), env=env, 
               stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
               universal_newlines=True)
            
            # Wait a bit and check output
            time.sleep(2)
            
            if process.poll() is None:
                print("✅ API process started successfully!")
                process.terminate()
                process.wait()
            else:
                print("❌ API process failed to start")
                output, _ = process.communicate()
                print(f"Error output: {output}")
                
        except Exception as e:
            print(f"Debug error: {e}")
            import traceback
            traceback.print_exc()
    
    def start_servers(self):
        """Start both API and frontend servers"""
        try:
            # Check dependencies
            if not self.check_dependencies():
                self.update_status("❌ Failed to install dependencies", "red")
                return False
            
            self.update_status("🔧 Starting API server...", "blue")
            
            # Start API server
            api_dir = Path("src/api").resolve()
            if not api_dir.exists():
                self.update_status("❌ API directory not found", "red")
                return False
            
            # Get current working directory and set up environment
            current_dir = Path.cwd()
            env = os.environ.copy()
            env['PYTHONPATH'] = str(current_dir)
            
            # Try uvicorn command first (what works in terminal)
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
                self.update_status(f"❌ API failed to start: {output[:100]}...", "red")
                return False
            
            self.update_status("🌐 Starting frontend server...", "blue")
            
            # Start frontend server
            frontend_dir = Path("frontend").resolve()
            if not frontend_dir.exists():
                self.update_status("❌ Frontend directory not found", "red")
                return False
                
            self.frontend_process = subprocess.Popen([
                sys.executable, "-m", "http.server", "3000"
            ], cwd=str(frontend_dir), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait a bit for frontend to start
            time.sleep(2)
            
            # Verify both processes are still running
            if self.api_process.poll() is not None:
                self.update_status("❌ API server stopped unexpectedly", "red")
                return False
                
            if self.frontend_process.poll() is not None:
                self.update_status("❌ Frontend server stopped unexpectedly", "red")
                return False
            
            return True
            
        except Exception as e:
            self.update_status(f"❌ Error: {str(e)}", "red")
            # Try to get more detailed error info
            if hasattr(self, 'api_process') and self.api_process:
                try:
                    output, error = self.api_process.communicate(timeout=1)
                    if output or error:
                        print(f"API Error Output: {output}")
                        print(f"API Error: {error}")
                except:
                    pass
            return False
    
    def start_application(self):
        """Start the application in a separate thread"""
        self.start_button.config(state='disabled')
        self.start_progress()
        
        def start_thread():
            if self.start_servers():
                self.servers_running = True
                self.update_status("✅ Servers running successfully!", "green")
                self.stop_button.config(state='normal')
                
                # Auto-open the PWA
                time.sleep(1)
                webbrowser.open("http://localhost:3000")
                
            else:
                self.start_button.config(state='normal')
                
            self.stop_progress()
        
        threading.Thread(target=start_thread, daemon=True).start()
    
    def stop_servers(self):
        """Stop both servers"""
        self.update_status("🛑 Stopping servers...", "orange")
        self.start_progress()
        
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
        self.stop_progress()
        self.update_status("✅ Servers stopped", "green")
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
    
    def on_closing(self):
        """Handle application closing"""
        if self.servers_running:
            if messagebox.askokcancel("Quit", "Stop servers and quit QuickLedger?"):
                self.stop_servers()
                self.root.destroy()
        else:
            self.root.destroy()
    
    def run(self):
        """Run the application"""
        self.root.mainloop()

if __name__ == "__main__":
    # Change to project root directory
    script_dir = Path(__file__).parent.parent
    os.chdir(script_dir)
    
    app = QuickLedgerLauncher()
    app.run()