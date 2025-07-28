
# QuickLedger

QuickLedger is a fast, intuitive, CLI-first expense tracker built with Python and Typer. Track your daily spending using natural language, export summaries, and optionally extend via a lightweight FastAPI backend.

---

## Features

- Add expenses via command line (`ledger add`)
- View by day, week, or custom date range
- Natural language support (e.g. `Bought food for 2000`)
- Summary and basic analytics
- Edit and delete entries
- Export to CSV
- Simple REST API (no auth yet)
- JSON-based storage (easy to inspect and backup)
- Pythonic, Typer-powered CLI with FastAPI backend

---

## Installation

You can use either `pip` (recommended for end users) or `poetry` (recommended for contributors or development setup).

### ✅ Option 1: Using pip (PyPI)

```bash
pip install quickledger
```

Then you can use it directly via:

```bash
ledger
```

### 🛠️ Option 2: Using Poetry (Development)

1. Clone the repo:

```bash
git clone https://github.com/chinyereunamba/ledger.git
cd ledger
```

2. Install dependencies:

```bash
poetry install
```

3. Run the CLI:

```bash
poetry run ledger
```

---

## CLI Commands

### ➕ Add Expense

```bash
ledger add
```

Supports natural language:

```bash
ledger say "Bought food for 1500"
```

### 📅 View Expenses

```bash
ledger view --date 2025-07-25
ledger view --week
ledger view --range 2025-07-01 2025-07-25
```

### ✏️ Edit or Delete

```bash
ledger edit --date 2025-07-24 --index 1
ledger delete --date 2025-07-24 --index 1
```

### 📤 Export

```bash
ledger export --path my_expenses.csv
```

---

## 🌐 API

Start the FastAPI server from the `api/` folder:

```bash
uvicorn main:app --reload
```

### Endpoints

| Method | Endpoint              | Description                    |
|--------|-----------------------|--------------------------------|
| GET    | `/expenses/`          | Get all expenses               |
| POST   | `/expenses/`          | Add a new expense              |
| GET    | `/expenses/{date}`    | Get expenses for a date        |
| DELETE | `/expenses/{date}`    | Delete all expenses for a date |
| GET    | `/summary/`           | Get total summary              |
| GET    | `/summary/{date}`     | Summary for a specific date    |
| GET    | `/summary/week`       | Past 7 days summary            |
| GET    | `/summary/range`      | Summary for a date range       |

⚠️ No authentication yet — intended for local/private use.

---

## 🧠 NLP Support

You can input expenses like:

```bash
ledger say "Paid for transport 700"
```

This is automatically parsed as:

- **Expense**: transport
- **Amount**: 700
- **Date**: today (default)

---

## 📂 Project Structure

```
ledger/
├── ledger/               # CLI logic & utilities
│   ├── ledger.py
│   ├── utils.py
│   └── constants.py
├── api/                  # FastAPI backend
│   ├── main.py
│   ├── routes/
│   │   └── __init__.py
│   └── models.py
├── ledger.json           # Local JSON storage
├── main.py
├── pyproject.toml        # Poetry config
├── README.md             # ← You're here
└── LICENSE
```

---

## 📦 PyPI

Coming soon to [PyPI](https://pypi.org/project/quickledger/) for easier installation via `pip`.

---

## 📃 License

MIT © 2025 [Chinyere Unamba](https://github.com/chinyereunamba/LICENSE)