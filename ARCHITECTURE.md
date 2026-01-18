# Ledger Architecture Documentation

## Overview

This document describes the refactored architecture of the QuickLedger application, following clean architecture principles with clear separation of concerns.

## Project Structure

```
ledger/
├── src/
│   ├── ledger/                    # Core package
│   │   ├── config/                # Configuration management
│   │   ├── domain/                # Domain models (pure Python)
│   │   ├── services/              # Business logic layer
│   │   ├── repositories/          # Data access layer
│   │   └── parsers/               # NLP parsing
│   ├── api/                       # API layer (FastAPI)
│   │   ├── models/                # API models (Pydantic)
│   │   ├── routes/                # API routes
│   │   ├── dependencies.py        # Dependency injection
│   │   └── main.py                # FastAPI app
│   └── cli/                       # CLI layer
│       ├── commands/               # CLI commands
│       ├── presenters/             # CLI presentation
│       └── main.py                 # CLI entry point
├── tests/                         # Test suite
│   ├── unit/                      # Unit tests
│   ├── integration/               # Integration tests
│   └── conftest.py                # Pytest fixtures
└── frontend/                      # Frontend (unchanged)
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

