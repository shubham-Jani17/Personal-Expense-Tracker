"""
database.py - Database Layer for Personal Expense Tracker
Handles SQLite database connection, initialization, and CRUD operations.
"""

import os
import sqlite3
from typing import List, Optional, Tuple, Dict, Any

# Define database directory and path relative to this file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "expenses.db")


def get_connection(db_path: str = DB_PATH) -> sqlite3.Connection:
    """
    Establishes and returns a connection to the SQLite database.
    Ensures that the target directory exists.
    """
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str = DB_PATH) -> None:
    """
    Initializes the SQLite database and creates the expenses table if it does not exist.
    Preserves all existing data if the table is already present.
    
    Table schema:
        - id: INTEGER PRIMARY KEY AUTOINCREMENT
        - title: TEXT NOT NULL
        - amount: REAL NOT NULL
        - category: TEXT NOT NULL
        - date: TEXT NOT NULL (YYYY-MM-DD)
    """
    conn = get_connection(db_path)
    try:
        with conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    amount REAL NOT NULL,
                    category TEXT NOT NULL,
                    date TEXT NOT NULL
                )
            """)
    finally:
        conn.close()


def insert_expense(title: str, amount: float, category: str, date: str, db_path: str = DB_PATH) -> int:
    """
    Inserts a new expense record into the expenses table.
    Returns the newly created expense ID.
    """
    conn = get_connection(db_path)
    try:
        with conn:
            cursor = conn.execute(
                """
                INSERT INTO expenses (title, amount, category, date)
                VALUES (?, ?, ?, ?)
                """,
                (title.strip(), float(amount), category.strip(), date.strip())
            )
            return cursor.lastrowid
    finally:
        conn.close()


def get_all_expenses(db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    """
    Retrieves all expense records sorted chronologically descending by date and ID.
    """
    conn = get_connection(db_path)
    try:
        cursor = conn.execute(
            "SELECT id, title, amount, category, date FROM expenses ORDER BY date DESC, id DESC"
        )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def get_expense_by_id(expense_id: int, db_path: str = DB_PATH) -> Optional[Dict[str, Any]]:
    """
    Retrieves a single expense by its unique ID.
    Returns None if not found.
    """
    conn = get_connection(db_path)
    try:
        cursor = conn.execute(
            "SELECT id, title, amount, category, date FROM expenses WHERE id = ?",
            (expense_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def update_expense(
    expense_id: int,
    title: str,
    amount: float,
    category: str,
    date: str,
    db_path: str = DB_PATH
) -> bool:
    """
    Updates an existing expense record by ID.
    Returns True if updated successfully, False if ID not found.
    """
    conn = get_connection(db_path)
    try:
        with conn:
            cursor = conn.execute(
                """
                UPDATE expenses
                SET title = ?, amount = ?, category = ?, date = ?
                WHERE id = ?
                """,
                (title.strip(), float(amount), category.strip(), date.strip(), expense_id)
            )
            return cursor.rowcount > 0
    finally:
        conn.close()


def delete_expense(expense_id: int, db_path: str = DB_PATH) -> bool:
    """
    Deletes an expense record by its ID.
    Returns True if deleted successfully, False if ID not found.
    """
    conn = get_connection(db_path)
    try:
        with conn:
            cursor = conn.execute(
                "DELETE FROM expenses WHERE id = ?",
                (expense_id,)
            )
            return cursor.rowcount > 0
    finally:
        conn.close()


def get_expenses_by_category(category: str, db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    """
    Retrieves all expense records matching a specific category (case-insensitive).
    """
    conn = get_connection(db_path)
    try:
        cursor = conn.execute(
            """
            SELECT id, title, amount, category, date
            FROM expenses
            WHERE LOWER(category) = LOWER(?)
            ORDER BY date DESC, id DESC
            """,
            (category.strip(),)
        )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def get_expenses_by_date_range(start_date: str, end_date: str, db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    """
    Retrieves expense records within the inclusive date range [start_date, end_date].
    """
    conn = get_connection(db_path)
    try:
        cursor = conn.execute(
            """
            SELECT id, title, amount, category, date
            FROM expenses
            WHERE date BETWEEN ? AND ?
            ORDER BY date DESC, id DESC
            """,
            (start_date.strip(), end_date.strip())
        )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def get_total_spent(db_path: str = DB_PATH) -> float:
    """
    Calculates the cumulative total amount of all recorded expenses.
    """
    conn = get_connection(db_path)
    try:
        cursor = conn.execute("SELECT COALESCE(SUM(amount), 0.0) FROM expenses")
        row = cursor.fetchone()
        return float(row[0]) if row else 0.0
    finally:
        conn.close()


def get_category_summary(db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    """
    Returns aggregated spending summary grouped by category, ordered from highest to lowest spent.
    """
    conn = get_connection(db_path)
    try:
        cursor = conn.execute(
            """
            SELECT category, COUNT(id) as count, COALESCE(SUM(amount), 0.0) as total
            FROM expenses
            GROUP BY category
            ORDER BY total DESC
            """
        )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def get_total_expenses_stats(db_path: str = DB_PATH) -> Dict[str, Any]:
    """
    Executes SQLite queries to retrieve overall expense metrics.
    Returns total spending, transaction count, average expense,
    category-wise spending, and highest overall expense.
    """
    conn = get_connection(db_path)
    try:
        cursor = conn.execute(
            """
            SELECT 
                COALESCE(SUM(amount), 0.0) AS total_spent,
                COUNT(id) AS transaction_count,
                COALESCE(AVG(amount), 0.0) AS avg_expense
            FROM expenses
            """
        )
        stats_row = cursor.fetchone()
        total_spent = float(stats_row["total_spent"]) if stats_row else 0.0
        count = int(stats_row["transaction_count"]) if stats_row else 0
        avg_expense = float(stats_row["avg_expense"]) if stats_row else 0.0

        cursor = conn.execute(
            """
            SELECT 
                category,
                COUNT(id) AS count,
                COALESCE(SUM(amount), 0.0) AS total
            FROM expenses
            GROUP BY category
            ORDER BY total DESC
            """
        )
        category_rows = [dict(r) for r in cursor.fetchall()]

        cursor = conn.execute(
            """
            SELECT id, title, amount, category, date
            FROM expenses
            ORDER BY amount DESC, id DESC
            LIMIT 1
            """
        )
        highest_row = cursor.fetchone()
        highest_expense = dict(highest_row) if highest_row else None

        return {
            "total_spent": round(total_spent, 2),
            "transaction_count": count,
            "average_expense": round(avg_expense, 2),
            "category_spending": category_rows,
            "highest_expense": highest_expense,
        }
    finally:
        conn.close()


def get_monthly_summary(year_month: str, db_path: str = DB_PATH) -> Dict[str, Any]:
    """
    Executes SQLite queries to retrieve monthly expense metrics for a specific month (YYYY-MM).
    Calculates total spending, transaction count, average expense,
    category-wise spending, and highest monthly expense.
    """
    conn = get_connection(db_path)
    try:
        # 1. Monthly total, count, and average
        cursor = conn.execute(
            """
            SELECT 
                COALESCE(SUM(amount), 0.0) AS total_spent,
                COUNT(id) AS transaction_count,
                COALESCE(AVG(amount), 0.0) AS avg_expense
            FROM expenses
            WHERE strftime('%Y-%m', date) = ?
            """,
            (year_month,)
        )
        stats_row = cursor.fetchone()
        total_spent = float(stats_row["total_spent"]) if stats_row else 0.0
        count = int(stats_row["transaction_count"]) if stats_row else 0
        avg_expense = float(stats_row["avg_expense"]) if stats_row else 0.0

        # 2. Monthly category-wise spending
        cursor = conn.execute(
            """
            SELECT 
                category,
                COUNT(id) AS count,
                COALESCE(SUM(amount), 0.0) AS total
            FROM expenses
            WHERE strftime('%Y-%m', date) = ?
            GROUP BY category
            ORDER BY total DESC
            """,
            (year_month,)
        )
        category_rows = [dict(r) for r in cursor.fetchall()]

        # 3. Monthly highest expense
        cursor = conn.execute(
            """
            SELECT id, title, amount, category, date
            FROM expenses
            WHERE strftime('%Y-%m', date) = ?
            ORDER BY amount DESC, id DESC
            LIMIT 1
            """,
            (year_month,)
        )
        highest_row = cursor.fetchone()
        highest_expense = dict(highest_row) if highest_row else None

        # 4. List of expenses in this month
        cursor = conn.execute(
            """
            SELECT id, title, amount, category, date
            FROM expenses
            WHERE strftime('%Y-%m', date) = ?
            ORDER BY date DESC, id DESC
            """,
            (year_month,)
        )
        expenses_rows = [dict(r) for r in cursor.fetchall()]

        return {
            "month": year_month,
            "total_spent": round(total_spent, 2),
            "transaction_count": count,
            "average_expense": round(avg_expense, 2),
            "category_spending": category_rows,
            "highest_expense": highest_expense,
            "expenses": expenses_rows,
        }
    finally:
        conn.close()


def get_distinct_months(db_path: str = DB_PATH) -> List[str]:
    """
    Retrieves all distinct YYYY-MM months containing recorded expenses.
    """
    conn = get_connection(db_path)
    try:
        cursor = conn.execute(
            """
            SELECT DISTINCT strftime('%Y-%m', date) AS month
            FROM expenses
            WHERE date IS NOT NULL AND date != ''
            ORDER BY month DESC
            """
        )
        return [row["month"] for row in cursor.fetchall() if row["month"]]
    finally:
        conn.close()


if __name__ == "__main__":
    print(f"Initializing database at: {DB_PATH}")
    init_db()
    print("Database initialization complete.")
