# QuickLedger

**QuickLedger** is a fast, intuitive, CLI-first expense tracker built with Python and Typer.  
Track your daily spending using natural language, export summaries, and optionally extend functionality via a lightweight FastAPI backend.

---

## Features

- Add expenses via command line (`ledger add`)
- View by day, week, or date range
- Natural language input (e.g. `Bought food for 2000`)
- Summary and analytics
- Edit and delete entries
- Export to CSV
- Simple REST API (no authentication yet)
- JSON-based storage (easy to inspect and back up)
- Pythonic, Typer-powered CLI with optional FastAPI backend
- Poetry-managed project

---

## Getting Started

1. **Clone the repository**

```bash
git clone https://github.com/chinyereunamba/ledger.git
cd ledger
```

2. **Install dependencies**

```bash
poetry install
```

3. **Run the CLI**

```bash
poetry run ledger
```

---

## CLI Usage

### Add Expense

```bash
ledger add
```

Or via natural language:

```bash
ledger say "Bought food for 1500"
```

### View Expenses

```bash
ledger view --date 2025-07-25
ledger view --week
ledger view --range 2025-07-01 2025-07-25
```

### Edit or Delete Entry

```bash
ledger edit --date 2025-07-24 --index 1
ledger delete --date 2025-07-24 --index 1
```

### Export to CSV

```bash
ledger export --path my_expenses.csv
```

---

## API (Optional)

To run the FastAPI server:

```bash
cd api
poetry run uvicorn main:app --reload
```

### Endpoints

| Method | Endpoint            | Description                      |
|--------|---------------------|----------------------------------|
| GET    | `/expenses/`        | Get all expenses                 |
| POST   | `/expenses/`        | Add a new expense                |
| GET    | `/expenses/{date}`  | Get expenses for a date          |
| DELETE | `/expenses/{date}`  | Delete all expenses for a date   |
| GET    | `/summary/`         | Get total summary                |
| GET    | `/summary/{date}`   | Summary for a specific date      |
| GET    | `/summary/week`     | Past 7 days summary              |
| GET    | `/summary/range`    | Summary for a date range         |

> **Note:** No authentication yet — intended for local use or behind a private proxy.

---

## Project Structure

```
ledger/
├── ledger/               # CLI logic and  utilities
│   ├── ledger.py
│   ├── utils.py
│   └── constants.py
├── api/                  # FastAPI backend
│   ├── main.py
│   ├── routes/
│   │   └── __init__.py
│   ├── models.py
├── pyproject.toml        # Poetry configuration
├── README.md             # You're here
└── LICENSE
```

---

## Natural Language Support

Log expenses conversationally:

```bash
ledger say "Paid for transport 700"
```

QuickLedger will automatically extract:
- **Expense**: transport  
- **Amount**: 700  
- **Date**: today (default)

---

## License

MIT © 2025 [Chinyere Unamba](https://github.com/chinyereunamba)