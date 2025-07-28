# Ledger API

A comprehensive FastAPI-based REST API for expense tracking and analytics.

## 🚀 Quick Start

### Installation

```bash
cd api
pip install -r requirements.txt
```

### Run the Server (Recommended)

```bash
# FastAPI development server with auto-reload
fastapi dev main.py
```

### Alternative Ways to Run

```bash
# Using the run script
python run.py

# Direct uvicorn
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📋 API Endpoints

### 📥 Expense Management

#### Add New Expense

```http
POST /expenses
Content-Type: application/json

{
  "expense": "Coffee",
  "amount": 5.50,
  "date": "2025-07-28"  // Optional, defaults to today
}
```

#### Get Expenses

```http
# Get all expenses
GET /expenses

# Get expenses for specific date
GET /expenses?date=2025-07-28

# Get expenses for current week
GET /expenses?week=true

# Get expenses for date range
GET /expenses?range=2025-07-01,2025-07-31
```

#### Edit Expense

```http
PUT /expenses/2025-07-28/0
Content-Type: application/json

{
  "expense": "Breakfast",  // Optional
  "amount": 12.50         // Optional
}
```

#### Delete Expense

```http
DELETE /expenses/2025-07-28/0
```

### 📊 Summaries & Analytics

#### Get Summary

```http
# All-time summary
GET /summary

# Summary for specific date
GET /summary?date=2025-07-28

# Summary for current week
GET /summary?week=true

# Summary for date range
GET /summary?range=2025-07-01,2025-07-31
```

#### Get Statistics

```http
GET /stats
```

Returns comprehensive analytics including:

- Total spent
- Daily average
- Most spent-on category
- Most frequent expense
- Most expensive day
- Top expenses and categories

## 📊 Response Examples

### Expense Response

```json
{
  "date": "2025-07-28",
  "expense": "Coffee",
  "amount": 5.5,
  "index": 0
}
```

### Summary Response

```json
{
  "total": 125.50,
  "expenses": [...],
  "period": "Date: 2025-07-28",
  "transaction_count": 5,
  "days_with_expenses": 3
}
```

### Stats Response

```json
{
  "total_spent": 1250.75,
  "daily_average": 41.69,
  "transaction_count": 45,
  "days_tracked": 30,
  "most_spent_category": {
    "name": "food",
    "amount": 450.25
  },
  "most_frequent_expense": {
    "name": "coffee",
    "count": 15
  },
  "most_expensive_day": {
    "date": "2025-07-15",
    "amount": 85.50
  },
  "top_expenses": [...],
  "top_categories": [...],
  "category_breakdown": {...}
}
```

## 🔧 Features

- **Automatic categorization** of expenses
- **Date range filtering** for all endpoints
- **Comprehensive analytics** with breakdowns
- **Input validation** and error handling
- **Interactive documentation** with Swagger UI
- **RESTful design** following best practices

## 🛠️ Development

### Project Structure

```
api/
├── main.py             # Main FastAPI application entry point
├── app.py              # Legacy app file (use main.py instead)
├── models.py           # Pydantic models for validation
├── utils.py            # Utility functions
├── routes/
│   ├── __init__.py     # Routes package
│   ├── expenses.py     # Expense management endpoints
│   ├── analytics.py    # Analytics and summary endpoints
│   └── utility.py      # Health check and info endpoints
├── run.py              # Alternative server startup script
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

### Error Handling

The API returns appropriate HTTP status codes:

- `200` - Success
- `400` - Bad Request (invalid input)
- `404` - Not Found (expense doesn't exist)
- `500` - Internal Server Error

### Data Storage

The API uses the same `~/.ledger/` directory structure as the CLI application, ensuring data consistency between interfaces.

## ⚡ Quick Commands

```bash
# Start development server (recommended)
fastapi dev main.py

# Add an expense via curl
curl -X POST "http://localhost:8000/expenses" \
  -H "Content-Type: application/json" \
  -d '{"expense": "Coffee", "amount": 5.50}'

# Get all expenses
curl "http://localhost:8000/expenses"

# Get comprehensive stats
curl "http://localhost:8000/stats"

# View interactive docs
open http://localhost:8000/docs
```
