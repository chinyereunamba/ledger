# Ledger Architecture Documentation

## Overview

This document describes the refactored architecture of the QuickLedger application, following clean architecture principles with clear separation of concerns.

## Project Structure

```
ledger/
├── src/                          # Source code
│   ├── ledger/                  # Core business logic
│   │   ├── config/              # Configuration management
│   │   ├── domain/              # Domain models
│   │   ├── services/             # Business logic layer
│   │   ├── repositories/        # Data access layer
│   │   └── parsers/             # NLP parsing
│   ├── api/                     # FastAPI application
│   │   ├── models/              # API models (Pydantic)
│   │   ├── routes/              # API routes
│   │   ├── dependencies.py      # Dependency injection
│   │   └── main.py              # FastAPI app entry point
│   └── cli/                     # CLI interface
│       ├── commands/            # CLI commands
│       ├── presenters/         # CLI presentation
│       └── main.py             # CLI entry point
│
├── tests/                        # Test suite
│   ├── unit/                    # Unit tests
│   ├── integration/             # Integration tests
│   └── conftest.py             # Pytest fixtures
│
├── frontend/                     # Frontend application
│   ├── js/                      # JavaScript files
│   ├── icons/                   # Application icons
│   └── index.html               # Main HTML file
│
├── scripts/                      # Development & utility scripts
│   ├── dev.py                   # Development server runner
│   ├── run.sh                   # Shell script runner
│   ├── quickledger-launcher.py  # GUI launcher
│   └── [other utility scripts]
│
├── docker/                       # Docker configuration
│   ├── Dockerfile.api          # API Docker image
│   ├── Dockerfile.frontend     # Frontend Docker image
│   └── docker-compose.yml     # Docker Compose config
│
├── config/                       # Application configuration
│   └── nginx.conf               # Nginx configuration
│
├── ledger/                       # Legacy compatibility
│   └── __init__.py             # Backward compatibility exports
│
├── Configuration Files (Root)
│   ├── pyproject.toml          # Poetry/Python package config
│   ├── poetry.lock             # Dependency lock file
│   ├── requirements.txt        # Python dependencies
│   ├── pytest.ini             # Pytest configuration
│   ├── package.json            # Node.js configuration
│   ├── Makefile                # Build automation
│   └── .gitignore              # Git ignore rules
│
└── Documentation
    ├── README.md               # Main documentation
    ├── ARCHITECTURE.md         # Architecture documentation
    └── LICENSE                 # License file
```

## Architecture Layers

### Domain Layer (`src/ledger/domain/`)

Pure Python data structures with no external dependencies:
- `expense.py`: Expense entity
- `category.py`: Category entity
- `budget.py`: Budget entities
- `user.py`: User entity

### Service Layer (`src/ledger/services/`)

Business logic orchestration:
- `expense_service.py`: Expense operations
- `category_service.py`: Category management
- `budget_service.py`: Budget management
- `analytics_service.py`: Statistics and analytics
- `user_service.py`: User management

### Repository Layer (`src/ledger/repositories/`)

Data persistence abstraction:
- `file_manager.py`: File operations and backups
- `expense_repository.py`: Expense data access
- `category_repository.py`: Category data access
- `budget_repository.py`: Budget data access
- `user_repository.py`: User data access

### API Layer (`src/api/`)

FastAPI application:
- Routes handle HTTP requests/responses
- Models define request/response schemas
- Dependency injection provides services
- No business logic in routes

### CLI Layer (`src/cli/`)

Command-line interface:
- Commands organized by domain
- Presenters handle Rich table formatting
- Calls services, not repositories

## Dependency Flow

```
CLI → Services → Repositories → File System
API → Services → Repositories → File System
     ↓
  Domain Models
```

## Key Improvements

1. **Separation of Concerns**: Business logic separated from presentation and data access
2. **Dependency Injection**: Services injected into API routes and CLI commands
3. **Centralized Configuration**: Single source of truth for file paths
4. **Type Safety**: Comprehensive type hints throughout
5. **Testability**: Services can be tested with mocked repositories
6. **No sys.path Hacks**: Proper Python package structure

## Migration Notes

The old `ledger/ledger.py` file is preserved for backward compatibility during migration. All new code uses the refactored architecture.

## Testing

- Unit tests: Test services in isolation with mocked repositories
- Integration tests: Test API routes and CLI commands end-to-end
- Fixtures: Reusable test data and temporary directories

## Configuration

All configuration is centralized in `src/ledger/config/`:
- File paths managed through `Paths` class
- Settings accessible via `get_settings()`
- Environment variable support for data directory

