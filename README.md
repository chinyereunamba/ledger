## 🧾 QuickLedger

A fast, intuitive, **CLI-first expense tracker** built with Python & Typer — track your daily spending using natural language, export summaries, and optionally extend via a lightweight API.

---

### ⚡ Features

* ✅ Add expenses via command line (`ledger add`)
* 📅 View by day, week, or range
* 🧠 Natural language support (e.g. `Bought food for 2000`)
* 📊 Summary and analytics
* 🧹 Edit and delete entries
* 📤 Export to CSV
* 🌐 Simple REST API (no auth yet)
* 📝 JSON-based storage (easy to inspect and backup)
* 🐍 Pythonic, Typer-powered CLI with FastAPI backend
* 📦 Poetry-managed project

---

### 🚀 Getting Started

#### 1. Clone the repo

```bash
git clone https://github.com/yourusername/quickledger.git
cd ledger
```

#### 2. Install dependencies

```bash
poetry install
```

#### 3. Run the CLI

```bash
poetry run ledger
```

---

### 🧑‍💻 CLI Commands

#### ➕ Add Expense

```bash
ledger add
```

Supports prompts or natural language:

```bash
ledger say "Bought food for 1500"
```

#### 📅 View Expenses

```bash
ledger view --date 2025-07-25
ledger view --week
ledger view --range 2025-07-01 2025-07-25
```

#### ✏️ Edit or Delete

```bash
ledger edit --date 2025-07-24 --index 1
ledger delete --date 2025-07-24 --index 1
```

#### 📤 Export

```bash
ledger export --path my_expenses.csv
```

---

### 🌐 API

Start the FastAPI server:

```bash
poetry run uvicorn api.main:app --reload
```

#### 🔗 Available Endpoints

| Method | Endpoint           | Description                    |
| ------ | ------------------ | ------------------------------ |
| GET    | `/expenses/`       | Get all expenses               |
| POST   | `/expenses/`       | Add a new expense              |
| GET    | `/expenses/{date}` | Get expenses for a date        |
| DELETE | `/expenses/{date}` | Delete all expenses for a date |
| GET    | `/summary/`        | Get total summary              |
| GET    | `/summary/{date}`  | Summary for a specific date    |
| GET    | `/summary/week`    | Past 7 days summary            |
| GET    | `/summary/range`   | Summary for date range         |

> ⚠️ No authentication yet — use locally or behind a private proxy.

---

### 📂 Project Structure

```
quickledger/
├── ledger/               # CLI logic & utils
│   ├── cli.py
│   ├── ledger.py
│   ├── utils.py
│   └── constants.py
├── api/                  # FastAPI backend
│   ├── main.py
│   ├── routes.py
│   ├── models.py
├── ledger.json           # Local JSON data
├── pyproject.toml        # Poetry config
├── README.md             # ← You're here
└── LICENSE
```

---

### 🧠 NLP Support

Supports inputs like:

```
ledger say "Paid for transport 700"
```

Automatically parses:

* Expense: `transport`
* Amount: `700`
* Date: `today` (by default)

---

### 📃 License

MIT © 2025 Chinyere Unamba

---