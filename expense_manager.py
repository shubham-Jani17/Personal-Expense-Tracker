"""
expense_manager.py - Business Logic Layer for Personal Expense Tracker
Manages validation, data sanitization, categories, and financial calculations.
"""

import os
import csv
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
import database


class ExpenseManager:
    # Allowed categories as required
    CATEGORIES = [
        "Food",
        "Transportation",
        "Shopping",
        "Entertainment",
        "Healthcare",
        "Education",
        "Bills",
        "Rent",
        "Travel",
        "Other"
    ]
    DEFAULT_CATEGORIES = CATEGORIES

    def __init__(self, db_path: Optional[str] = None):
        """
        Initializes the ExpenseManager and ensures database table setup.
        Preserves existing data.
        """
        self.db_path = db_path or database.DB_PATH
        database.init_db(self.db_path)

    @staticmethod
    def validate_title(title: str) -> str:
        
        if not title or not title.strip():
            raise ValueError("Expense title cannot be empty.")
        return title.strip()

    @staticmethod
    def validate_amount(amount: Any) -> float:

        if amount is None:
            raise ValueError("Amount cannot be empty.")
        amt_str = str(amount).strip().lstrip("$").replace(",", "").strip()
        try:
            val = float(amt_str)
        except (ValueError, TypeError):
            raise ValueError("Amount must be a valid numeric value.")
        if val <= 0:
            raise ValueError("Amount must be greater than zero.")
        return round(val, 2)

    @classmethod
    def validate_category(cls, category: Any) -> str:
        
        if category is None or not str(category).strip():
            raise ValueError(f"Expense category cannot be empty. Allowed: {', '.join(cls.CATEGORIES)}")

        cat_str = str(category).strip()
        # Support 1-based index selection
        if cat_str.isdigit():
            idx = int(cat_str)
            if 1 <= idx <= len(cls.CATEGORIES):
                return cls.CATEGORIES[idx - 1]
            raise ValueError(f"Category number must be between 1 and {len(cls.CATEGORIES)}.")

        # Case-insensitive match
        for allowed in cls.CATEGORIES:
            if cat_str.lower() == allowed.lower():
                return allowed

        raise ValueError(
            f"Invalid category '{cat_str}'. Must be one of: {', '.join(cls.CATEGORIES)}"
        )

    @staticmethod
    def validate_date(date_str: Optional[str] = None) -> str:
       
        if not date_str or not str(date_str).strip():
            return datetime.now().strftime("%Y-%m-%d")

        cleaned = str(date_str).strip()
        try:
            parsed = datetime.strptime(cleaned, "%Y-%m-%d")
            return parsed.strftime("%Y-%m-%d")
        except ValueError:
            raise ValueError(f"Invalid date '{cleaned}'. Date must be in YYYY-MM-DD format (e.g., 2026-11-18).")

    @staticmethod
    def validate_month(month_str: Optional[str] = None) -> str:
        
        if not month_str or not str(month_str).strip():
            return datetime.now().strftime("%Y-%m")

        cleaned = str(month_str).strip()
        try:
            parsed = datetime.strptime(cleaned, "%Y-%m")
            return parsed.strftime("%Y-%m")
        except ValueError:
            raise ValueError(f"Invalid month format '{cleaned}'. Expected YYYY-MM (e.g., 2026-11).")

    def add_expense(
        self,
        title: str,
        amount: float,
        category: str,
        date: Optional[str] = None
    ) -> Dict[str, Any]:
        
        valid_title = self.validate_title(title)
        valid_amount = self.validate_amount(amount)
        valid_category = self.validate_category(category)
        valid_date = self.validate_date(date)

        new_id = database.insert_expense(
            title=valid_title,
            amount=valid_amount,
            category=valid_category,
            date=valid_date,
            db_path=self.db_path
        )

        return {
            "id": new_id,
            "title": valid_title,
            "amount": valid_amount,
            "category": valid_category,
            "date": valid_date
        }

    def list_expenses(self) -> List[Dict[str, Any]]:
       
        return database.get_all_expenses(db_path=self.db_path)

    def get_expense(self, expense_id: int) -> Optional[Dict[str, Any]]:
       
        try:
            exp_id = int(expense_id)
        except (ValueError, TypeError):
            raise ValueError("Expense ID must be an integer.")
        return database.get_expense_by_id(exp_id, db_path=self.db_path)

    def update_expense(
        self,
        expense_id: int,
        title: Optional[str] = None,
        amount: Optional[float] = None,
        category: Optional[str] = None,
        date: Optional[str] = None
    ) -> bool:
       
        existing = self.get_expense(expense_id)
        if not existing:
            return False

        updated_title = self.validate_title(title) if title is not None else existing["title"]
        updated_amount = self.validate_amount(amount) if amount is not None else existing["amount"]
        updated_category = self.validate_category(category) if category is not None else existing["category"]
        updated_date = self.validate_date(date) if date is not None else existing["date"]

        return database.update_expense(
            expense_id=int(expense_id),
            title=updated_title,
            amount=updated_amount,
            category=updated_category,
            date=updated_date,
            db_path=self.db_path
        )

    def delete_expense(self, expense_id: int) -> bool:
        
        try:
            exp_id = int(expense_id)
        except (ValueError, TypeError):
            raise ValueError("Expense ID must be an integer.")
        return database.delete_expense(exp_id, db_path=self.db_path)

    def filter_by_category(self, category: str) -> List[Dict[str, Any]]:
        
        valid_cat = self.validate_category(category)
        return database.get_expenses_by_category(valid_cat, db_path=self.db_path)

    def search_by_category(self, category: str) -> Dict[str, Any]:
      
        valid_cat = self.validate_category(category)
        expenses = database.get_expenses_by_category(valid_cat, db_path=self.db_path)
        count = len(expenses)
        total_spent = sum(float(r["amount"]) for r in expenses)
        avg_expense = round(total_spent / count, 2) if count > 0 else 0.0

        return {
            "category": valid_cat,
            "expenses": expenses,
            "count": count,
            "total_spent": round(total_spent, 2),
            "average_expense": avg_expense,
        }

    def filter_by_date_range(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        
        valid_start = self.validate_date(start_date)
        valid_end = self.validate_date(end_date)
        if valid_start > valid_end:
            raise ValueError("Start date cannot be after end date.")
        return database.get_expenses_by_date_range(valid_start, valid_end, db_path=self.db_path)

    def calculate_total_expenses(self) -> Dict[str, Any]:
       
        stats = database.get_total_expenses_stats(db_path=self.db_path)
        total_spent = stats["total_spent"]

        # Calculate percentage for each category
        for cat in stats["category_spending"]:
            cat_total = float(cat["total"])
            cat["percentage"] = round((cat_total / total_spent * 100), 1) if total_spent > 0 else 0.0

        return stats

    def get_monthly_summary(self, month_str: Optional[str] = None) -> Dict[str, Any]:
     
        valid_month = self.validate_month(month_str)
        month_name = datetime.strptime(valid_month, "%Y-%m").strftime("%B %Y")

        summary = database.get_monthly_summary(valid_month, db_path=self.db_path)
        monthly_total = summary["total_spent"]

        # Compute category percentages for this month
        for cat in summary["category_spending"]:
            cat_total = float(cat["total"])
            cat["percentage"] = round((cat_total / monthly_total * 100), 1) if monthly_total > 0 else 0.0

        summary["month_name"] = month_name
        return summary

    def get_available_months(self) -> List[str]:
        
        return database.get_distinct_months(db_path=self.db_path)

    def export_to_csv(self, filepath: str = "expenses_export.csv") -> int:
       
        expenses = self.list_expenses()
        headers = ["ID", "Title", "Amount", "Category", "Date"]

        # Ensure directory exists if a folder path is included
        dirname = os.path.dirname(filepath)
        if dirname:
            os.makedirs(dirname, exist_ok=True)

        with open(filepath, mode="w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)
            for r in expenses:
                writer.writerow([
                    r["id"],
                    r["title"],
                    f"{float(r['amount']):.2f}",
                    r["category"],
                    r["date"]
                ])

        return len(expenses)

    def get_summary(self) -> Dict[str, Any]:
        
        return self.calculate_total_expenses()
