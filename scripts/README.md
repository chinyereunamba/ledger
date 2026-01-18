# Scripts Directory

This directory contains development and utility scripts for the QuickLedger project.

## Development Scripts

- `dev.py` - Development server runner (starts both API and frontend)
- `run.sh` - Shell script to run development servers
- `restart_frontend.sh` - Restart frontend server

## Launcher Scripts

- `quickledger-launcher.py` - GUI launcher for desktop app
- `quickledger-cli-launcher.py` - CLI launcher for desktop app

## Desktop App Scripts

- `create-desktop-entry.sh` - Create desktop entry file
- `install-desktop-app.sh` - Install desktop application
- `uninstall-desktop-app.sh` - Uninstall desktop application

## Usage

Most scripts can be run directly:
```bash
# Development server
python scripts/dev.py

# Or use Makefile
make dev
```

