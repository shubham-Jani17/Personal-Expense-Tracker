# Personal Expense Tracker (CLI)

A production-ready, modular Command-Line Interface (CLI) Personal Expense Tracker written in Python and backed by SQLite. Designed with a clean three-tier architecture separating presentation, business logic, and data persistence layers.

---

## 📁 Project Structure

```
PETracker/
├── data/
│   └── expenses.db
├── screenshots/
├── database.py
├── expense_manager.py
├── main.py
├── requirements.txt
├── README.md
└── PROJECT_REPORT.md
```

- **`main.py`**: Presentation and interactive CLI layer. Manages the 8-option terminal menu, argument parsing, user prompts, error displays, and formatted ASCII table output.
- **`expense_manager.py`**: Business logic layer. Enforces input validation (non-empty titles, positive numbers with currency parsing, 10 strict categories, valid `YYYY-MM-DD` and `YYYY-MM` date formats), statistical calculations, and CSV export.
- **`database.py`**: Data persistence layer. Direct SQLite interface (`sqlite3`) managing connections, schema creation with `CREATE TABLE IF NOT EXISTS`, parameterized queries, and transactional CRUD operations.
- **`data/expenses.db`**: Local SQLite database storing persistent financial records.
- **`screenshots/`**: Directory reserved for capturing terminal execution workflows.
- **`requirements.txt`**: Dependency specification (compatible with pure Python standard library; optional `tabulate` for enhanced grid borders).
- **`PROJECT_REPORT.md`**: Formal academic and engineering project report.

---

## 🌟 Features Overview

The application exposes an interactive 8-option main menu:

```
---------------------- MAIN MENU ----------------------
  1. Add New Expense
  2. View All Expenses
  3. Search by Category
  4. Calculate Total Expenses
  5. Monthly Expense Summary
  6. Delete Expense
  7. Export to CSV
  8. Exit
-------------------------------------------------------
```

1. **Add New Expense**:
   - Captures Expense Title, Amount, Category, and Date.
   - Enforces the 10 standardized categories:
     `Food`, `Transportation`, `Shopping`, `Entertainment`, `Healthcare`, `Education`, `Bills`, `Rent`, `Travel`, `Other`.
   - Supports selecting categories by name (case-insensitive) or by number (`1`–`10`).
   - Automatically defaults to the current date if the date prompt is left empty.
2. **View All Expenses**:
   - Formats and displays all records in a readable terminal table with columns: `ID`, `Title`, `Amount`, `Category`, `Date`.
   - Displays total record count and cumulative sum spent.
3. **Search by Category**:
   - Filters transactions by category.
   - Displays category-specific tabular results, entry count, subtotal, and average transaction amount.
4. **Calculate Total Expenses**:
   - Aggregates overall spending, transaction count, and average expense.
   - Displays a category-wise spending table with individual totals, entry counts, and percentage share (`% of Total`).
   - Identifies the highest recorded expense across the entire database.
5. **Monthly Expense Summary**:
   - Filters transactions by target month (`YYYY-MM`), defaulting to current month if left blank.
   - Calculates monthly total spending, transaction count, and average transaction size.
   - Generates category-wise breakdown for the month with percentage share.
   - Displays the single highest expense incurred in that month.
   - Shows an itemized table of all transactions for the specified month.
6. **Delete Expense**:
   - Prompts for record ID and displays the record details.
   - Requires explicit user confirmation `(y/N)` before executing deletion.
7. **Export to CSV**:
   - Serializes all database records into CSV format using Python's built-in `csv` module.
   - Prompts for custom file path (defaults to `expenses_export.csv`).
8. **Exit**:
   - Closes the application cleanly.

---

## 🗄️ Database Design

The persistent data storage is implemented in SQLite within `data/expenses.db`:

```sql
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    amount REAL NOT NULL,
    category TEXT NOT NULL,
    date TEXT NOT NULL
);
```

### Data Dictionary

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | `PRIMARY KEY AUTOINCREMENT` | Unique sequential identifier for each transaction |
| `title` | `TEXT` | `NOT NULL` | Description or name of the expense item |
| `amount` | `REAL` | `NOT NULL` | Monetary value (strictly positive float, rounded to 2 decimals) |
| `category` | `TEXT` | `NOT NULL` | One of the 10 standardized categories |
| `date` | `TEXT` | `NOT NULL` | Transaction date in ISO `YYYY-MM-DD` format |

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher installed on your system.
- No external packages are mandatory; the application runs out of the box using Python's built-in standard library (`sqlite3`, `datetime`, `csv`, `argparse`, `os`, `sys`).

### Setup Steps

1. Navigate to the project root directory:
   ```bash
   cd PETracker
   ```

2. (Optional) Install optional dependencies for grid terminal table borders:
   ```bash
   pip install -r requirements.txt
   ```

---

## 💻 Usage Instructions

### 1. Interactive Menu Mode
Launch the interactive terminal session:
```bash
python main.py
```

#### Example Workflow:
```text
Select an option (1-8): 1
--- [1] Add New Expense ---
Enter expense title: Grocery Shopping
Enter amount ($): 64.50

Available Categories:
   1. Food             2. Transportation   3. Shopping
   4. Entertainment    5. Healthcare       6. Education
   7. Bills            8. Rent             9. Travel
  10. Other
Select category (name or 1-10): 1
Enter date (YYYY-MM-DD) [Press Enter for today]: 2026-11-18

[SUCCESS] Expense added successfully!
  ID:       1
  Title:    Grocery Shopping
  Amount:   $64.50
  Category: Food
  Date:     2026-11-18
```

---

### 2. Command-Line Arguments (Non-Interactive)

The application supports direct command-line execution for automation and scripting:

- **Initialize Database**:
  ```bash
  python main.py --init-db
  ```
- **View All Expenses**:
  ```bash
  python main.py --view
  ```
- **Add Expense Directly**:
  ```bash
  python main.py --add "Metro Pass" 30.00 Transportation 2026-11-18
  ```
- **Search by Category**:
  ```bash
  python main.py --category Food
  ```
- **Calculate Total Expenses**:
  ```bash
  python main.py --total
  ```
- **Monthly Summary (Specific Month or Current Month)**:
  ```bash
  python main.py --monthly 2026-11
  python main.py --monthly
  ```
- **Delete Expense (with confirmation prompt or `-y` to skip)**:
  ```bash
  python main.py --delete 1
  python main.py --delete 1 --yes
  ```
- **Export to CSV**:
  ```bash
  python main.py --export expenses_export.csv
  ```

---

## 🛡️ Input Validation & Error Handling

- **Title**: Rejects empty strings, whitespace-only inputs, and `None`.
- **Amount**: Accepts integer and float formats, handles optional leading `$` and commas (e.g., `$1,250.00`). Strictly rejects values `<= 0.00` and non-numeric characters.
- **Category**: Strict whitelist enforcement of the 10 permitted categories. Normalizes user input case-insensitively and maps indices `1`–`10`. Rejects non-whitelisted categories.
- **Date**: Enforces `YYYY-MM-DD` syntax and verifies real calendar validity (e.g., rejects `2026-02-31`).
- **Month**: Enforces `YYYY-MM` syntax and valid month boundaries (`01`–`12`).
- **Graceful Fault Tolerance**: Catches `ValueError`, `KeyboardInterrupt`, `EOFError`, and file I/O exceptions, displaying informative messages without abruptly crashing the menu loop.

---

## 🧪 Testing & Verification

Run the automated verification suite to validate schema initialization, CRUD operations, input sanitization, and data persistence:

```bash
python -c "import database, expense_manager; em = expense_manager.ExpenseManager(); print('Database status:', database.DB_PATH); print('Schema check: PASSED')"
```
