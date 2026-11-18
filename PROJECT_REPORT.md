# Engineering Project Report: Personal Expense Tracker (CLI)

---

## 1. Abstract

The **Personal Expense Tracker** is a modular, offline-first command-line interface (CLI) software application developed in Python and backed by SQLite. The application addresses the ubiquitous need for personal financial visibility, record-keeping, and budgetary discipline. Built upon a robust three-tier software architecture, the system provides comprehensive expense tracking, strict input validation across 10 standardized categories, multi-faceted filtering, analytical reporting (including overall totals, category-wise breakdowns, and monthly expense summaries), and data export via Python's standard `csv` module. Persistent data storage is guaranteed through an SQLite relational database with transactional data integrity. The application operates without requiring external dependencies, ensuring maximum portability, security, and low-latency performance.

---

## 2. Objectives

The primary objectives of this project are:
1. **Persistent Data Storage**: Establish an isolated, relational SQLite database layer (`data/expenses.db`) that ensures persistent, transactional data storage across application sessions.
2. **Defensive Input Validation**: Implement strict validation on financial amounts (`> 0.00`), descriptions, dates (`YYYY-MM-DD`), and a standardized taxonomy of 10 expense categories.
3. **Core CRUD Functionalities**: Enable users to seamlessly add, inspect in tabular format, update, search, and delete expense records with user-safe confirmation prompts.
4. **Analytical Intelligence**: Implement financial aggregation algorithms to compute cumulative spending, transaction frequencies, average expenditures, percentage distributions by category, and single-highest transaction identification across all records and on a monthly basis (`YYYY-MM`).
5. **Data Portability**: Enable complete data export to standard Comma-Separated Values (CSV) format using Python's native `csv` module for auditing, archiving, and spreadsheet integration.
6. **Architectural Separation of Concerns**: Maintain clean structural boundaries across Presentation (`main.py`), Business Logic (`expense_manager.py`), and Persistence (`database.py`).

---

## 3. Requirements Specification

### 3.1 Functional Requirements

- **FR1: Record Ingestion**: The system shall accept expense title, positive amount, category, and date. If date is omitted, the system shall default to the current system date.
- **FR2: Category Enforcement**: The system shall restrict categories strictly to:
  `Food`, `Transportation`, `Shopping`, `Entertainment`, `Healthcare`, `Education`, `Bills`, `Rent`, `Travel`, `Other`.
  The system shall support input by name (case-insensitive) or by number (`1`–`10`).
- **FR3: Tabular Display**: The system shall render records in an aligned terminal table featuring `ID`, `Title`, `Amount ($)`, `Category`, and `Date`.
- **FR4: Category Search**: The system shall allow users to search records by category and display matching records along with category subtotal, count, and average transaction amount.
- **FR5: Aggregate Spending Calculations**: The system shall calculate overall cumulative spending, total transaction count, average expense, category-wise expenditure with percentages (`% of Total`), and the highest expense.
- **FR6: Monthly Expense Summary**: The system shall allow filtering by month (`YYYY-MM`), computing monthly total spending, transaction count, average expense, category-wise breakdown with percentages, highest monthly expense, and an itemized monthly transaction table.
- **FR7: Record Deletion**: The system shall require the user to provide an Expense ID and explicitly confirm deletion (`y/N`) before removing the record from SQLite.
- **FR8: CSV Export**: The system shall export all database records to a user-specified or default CSV file (`expenses_export.csv`) with standard column headers.
- **FR9: Continuous Execution**: The CLI menu shall remain active and re-display after each operation until the user explicitly selects Option 8 (Exit).

### 3.2 Non-Functional Requirements

- **NFR1: Portability & Zero Dependencies**: The core system shall operate using Python's Standard Library (`sqlite3`, `datetime`, `csv`, `argparse`, `os`, `sys`), eliminating external runtime requirements.
- **NFR2: Data Integrity & Persistence**: Database transactions shall use ACID-compliant SQLite operations with parameterized queries to prevent SQL injection and data corruption.
- **NFR3: Fault Tolerance**: Invalid inputs (e.g., negative values, malformed dates like `2026-02-31`, non-existent IDs) shall be intercepted gracefully with clear error messages without terminating the interactive loop.
- **NFR4: Performance**: Database queries, table renderings, and calculations shall execute in under 50 milliseconds for typical personal finance workloads.

---

## 4. System Architecture

The application adopts a **Three-Tier Architectural Pattern**:

```
+---------------------------------------------------------------+
|                      Presentation Layer                       |
|                           (main.py)                           |
|  - Interactive 8-Option CLI Menu Loop                         |
|  - Command-Line Argument Flags (--init-db, --view, etc.)      |
|  - ASCII Table Formatter & User Prompt Handlers               |
+-------------------------------+-------------------------------+
                                |
                                v
+---------------------------------------------------------------+
|                     Business Logic Layer                      |
|                     (expense_manager.py)                      |
|  - Input Validation (Amount > 0, 10 Categories, Date/Month)   |
|  - Financial Aggregations & Percentage Distribution Math      |
|  - CSV Serialization via Python 'csv' Module                  |
+-------------------------------+-------------------------------+
                                |
                                v
+---------------------------------------------------------------+
|                    Data Persistence Layer                     |
|                        (database.py)                          |
|  - SQLite Connection Management & PRAGMA Settings             |
|  - Table Schema DDL (CREATE TABLE IF NOT EXISTS)              |
|  - Parameterized CRUD SQL Statements & Aggregation Queries    |
+-------------------------------+-------------------------------+
                                |
                                v
+---------------------------------------------------------------+
|                      Persistent Storage                       |
|                      (data/expenses.db)                       |
+---------------------------------------------------------------+
```

### Data Flow Overview:
1. **User Request**: User selects an option from the menu or issues a CLI flag.
2. **Presentation**: `main.py` parses arguments or prompts the user for fields (`title`, `amount`, `category`, `date`).
3. **Validation & Processing**: `expense_manager.py` sanitizes inputs, enforces constraints, and calculates metrics.
4. **Database Execution**: `database.py` generates parameterized SQL queries and commits transactions to `data/expenses.db`.
5. **Response Display**: Resulting tuples/dictionaries are formatted into tabular terminal output and returned to the user.

---

## 5. Database Design & Relational Schema

The persistent data storage is implemented in an SQLite relational database located at `data/expenses.db`.

### 5.1 DDL (Data Definition Language) Schema
```sql
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    amount REAL NOT NULL,
    category TEXT NOT NULL,
    date TEXT NOT NULL
);
```

### 5.2 Data Dictionary

| Column Name | Data Type | Nullable | Primary Key | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | No | Yes (`AUTOINCREMENT`) | Unique sequential identifier assigned to each record |
| `title` | `TEXT` | No | No | Brief memo or description of the expenditure |
| `amount` | `REAL` | No | No | Numeric expenditure value (strictly positive float) |
| `category` | `TEXT` | No | No | Standardized category classification |
| `date` | `TEXT` | No | No | Transaction date in ISO-8601 (`YYYY-MM-DD`) |

### 5.3 Preservation & Schema Safety
The initialization function executes `CREATE TABLE IF NOT EXISTS`, ensuring that pre-existing data is preserved whenever the application starts, while ensuring the table and directories exist before any read/write operations occur.

---

## 6. Implementation Details

### 6.1 `database.py` (Persistence Layer)
- **`get_connection(db_path)`**: Resolves database path relative to `__file__`, ensures parent folder `data/` exists, and returns connection with `conn.row_factory = sqlite3.Row`.
- **`init_db(db_path)`**: Executes idempotent table creation.
- **`insert_expense(...)`**: Executes parameterized `INSERT INTO expenses (title, amount, category, date) VALUES (?, ?, ?, ?)`, returning `cursor.lastrowid`.
- **`get_all_expenses(...)`**: Retrieves all records sorted chronologically (`ORDER BY date DESC, id DESC`).
- **`delete_expense(expense_id)`**: Executes parameterized deletion returning boolean success.
- **`get_expenses_by_category(category)`**: Case-insensitive filtering using `LOWER(category) = LOWER(?)`.
- **`get_total_expenses_stats(...)`**: Uses SQLite SQL aggregates (`SUM`, `COUNT`, `AVG`, `GROUP BY`) to fetch overall total spent, transaction count, average, category breakdown, and highest expense in a single structured call.
- **`get_monthly_summary(year_month)`**: Leverages SQLite's `strftime('%Y-%m', date) = ?` to compute monthly spending metrics, category breakdown, and highest monthly transaction.
- **`get_distinct_months()`**: Retrieves distinct transaction months (`strftime('%Y-%m', date)`).

### 6.2 `expense_manager.py` (Business Logic Layer)
- **`validate_title(title)`**: Enforces non-empty, non-whitespace strings.
- **`validate_amount(amount)`**: Strips optional `$` and commas, validates float conversion, and checks `amount > 0.00`.
- **`validate_category(category)`**: Strictly checks against the 10 allowed categories. Maps numeric indices (`1`–`10`) and matches names case-insensitively.
- **`validate_date(date_str)`**: Uses `datetime.strptime(cleaned, "%Y-%m-%d")` to ensure valid calendar dates, defaulting to `datetime.now().strftime("%Y-%m-%d")` if empty.
- **`validate_month(month_str)`**: Uses `datetime.strptime(cleaned, "%Y-%m")` to ensure valid month format (`YYYY-MM`).
- **`calculate_total_expenses()`**: Calculates overall stats and derives category percentage shares (`% of Total`).
- **`get_monthly_summary(month_str)`**: Derives human-friendly month names (e.g., *"November 2026"*), monthly statistics, category percentages, and itemized monthly transactions.
- **`export_to_csv(filepath)`**: Uses Python's built-in `csv.writer` to write column headers (`ID`, `Title`, `Amount`, `Category`, `Date`) and row data.

### 6.3 `main.py` (Presentation Layer)
- **`format_table(rows)`**: Renders clean ASCII tables with dynamic column width calculations and borders (optionally using `tabulate` if installed).
- **`format_category_table(breakdown)`**: Formats category distribution tables with entry counts, total amounts, and percentage shares.
- **`interactive_mode(manager)`**: The main application loop presenting the 8 menu options, capturing inputs, routing to handlers, and catching `KeyboardInterrupt` and `EOFError`.
- **`main()` (CLI Interface)**: Uses `argparse` to allow direct execution of actions (`--init-db`, `--view`, `--add`, `--delete`, `--category`, `--total`, `--monthly`, `--export`).

---

## 7. Verification & Testing

### 7.1 Testing Methodology
Automated and manual test suites were executed covering:
1. **Database Schema & Integrity**: Executed SQLite `PRAGMA integrity_check;` to verify database structure.
2. **Data Persistence Across Sessions**: Inserted records, destroyed the manager instance, and re-instantiated a new manager session to confirm SQLite persistence.
3. **Boundary & Negative Input Validation**:
   - Empty/whitespace titles -> Intercepted with `ValueError`.
   - Non-numeric amounts, zero amounts, and negative values -> Intercepted with `ValueError`.
   - Non-whitelisted category names and out-of-range indices -> Intercepted with `ValueError`.
   - Invalid dates (e.g., `2026-02-30`, `18/11/2026`) and months (e.g., `2026-15`) -> Intercepted with `ValueError`.
4. **Mathematical Accuracy of Calculations**:
   - Overall cumulative sums and averages tested against multi-month datasets.
   - Monthly category percentages confirmed to total 100%.
   - Empty database and zero-transaction months confirmed to return `$0.00` without `ZeroDivisionError`.
5. **Deletion & Confirmation Logic**:
   - Cancellation (`n`) verified to leave records untouched.
   - Confirmation (`y`) verified to delete target record.
6. **CSV Export Integrity**:
   - Verified file creation, header structure, row counts, and data formatting using Python's `csv.reader`.

### 7.2 Test Summary Table

| Test Case | Target Feature | Input Data | Expected Result | Status |
| :--- | :--- | :--- | :--- | :--- |
| **TC01** | Database Init | `init_db()` | Schema created, existing data preserved | **PASSED** |
| **TC02** | Input Validation | Title: `""`, Amount: `-10` | Rejected with descriptive error | **PASSED** |
| **TC03** | Category Validation | Category: `"Crypto"` | Rejected; requires 1 of 10 categories | **PASSED** |
| **TC04** | Date Validation | Date: `"2026-02-30"` | Rejected (non-existent calendar date) | **PASSED** |
| **TC05** | Add Expense | `"Dinner"`, `45.50`, `"Food"` | Inserted, ID returned, persisted | **PASSED** |
| **TC06** | View Expenses | Database with records | Readable ASCII terminal table output | **PASSED** |
| **TC07** | Search Category | Category: `"Food"` | Matching rows, subtotal, and average | **PASSED** |
| **TC08** | Total Expenses | Multi-record dataset | Total, count, avg, category breakdown % | **PASSED** |
| **TC09** | Monthly Summary | Target: `"2026-11"` | Isolated monthly total, breakdown, highest | **PASSED** |
| **TC10** | Empty Month | Target: `"2027-01"` | Zero totals, count: 0, no division error | **PASSED** |
| **TC11** | Delete Expense | ID: `1`, Confirm: `'y'` | Record deleted from SQLite | **PASSED** |
| **TC12** | CSV Export | Target: `test.csv` | Valid CSV file with headers & rows | **PASSED** |
| **TC13** | Menu Loop | Option: `8` | Graceful exit without stack trace | **PASSED** |

---

## 8. Results & Performance

- **Persistence Verified**: Data persists reliably in `data/expenses.db` across all application restarts.
- **Terminal Readability**: Tables and metrics format cleanly across standard terminal widths.
- **Portability**: Verified zero external dependencies required; application runs purely on Python standard library.
- **Zero Structure Overhead**: No unauthorized files or folders were created; structure strictly maintained.

---

## 9. Conclusion & Future Roadmap

The **Personal Expense Tracker CLI** successfully delivers a robust, user-friendly, and persistent financial tracking solution. Its modular architecture ensures maintainability and extensibility.

### Future Roadmap
1. **Budget Threshold Alerts**: Add monthly category budget caps with automated warning alerts when spending exceeds 90%.
2. **Data Visualization**: Generate ASCII terminal sparklines or optional chart exports using Matplotlib.
3. **Recurring Expenses**: Support scheduled recurring entries (e.g., monthly rent, recurring subscription bills).
4. **JSON / Excel Export**: Extend data export capabilities to JSON and Excel (`.xlsx`) formats.
