"""
main.py - CLI Interface for Personal Expense Tracker
Provides an interactive command-line interface for managing expenses.
"""

import sys
import argparse
from datetime import datetime
from typing import List, Dict, Any, Optional
from expense_manager import ExpenseManager


def format_table(rows: List[Dict[str, Any]]) -> str:
    """
    Renders a formatted ASCII table for expense records.
    Uses 'tabulate' if available, otherwise renders a clean built-in grid.
    """
    if not rows:
        return "No expense records found."

    headers = ["ID", "Title", "Amount", "Category", "Date"]

    try:
        from tabulate import tabulate
        table_data = [
            [r["id"], r["title"], f"${float(r['amount']):.2f}", r["category"], r["date"]]
            for r in rows
        ]
        return tabulate(table_data, headers=headers, tablefmt="grid")
    except ImportError:
        # Built-in readable terminal table formatter
        col_widths = {
            "id": max(len("ID"), max(len(str(r["id"])) for r in rows)),
            "title": max(len("Title"), max(len(str(r["title"])) for r in rows)),
            "amount": max(len("Amount"), max(len(f"${float(r['amount']):.2f}") for r in rows)),
            "category": max(len("Category"), max(len(str(r["category"])) for r in rows)),
            "date": max(len("Date"), max(len(str(r["date"])) for r in rows)),
        }

        # Separator line
        sep = "+-" + "-+-".join("-" * col_widths[k] for k in ["id", "title", "amount", "category", "date"]) + "-+"

        # Header row
        header_str = (
            f"| {headers[0].ljust(col_widths['id'])} "
            f"| {headers[1].ljust(col_widths['title'])} "
            f"| {headers[2].ljust(col_widths['amount'])} "
            f"| {headers[3].ljust(col_widths['category'])} "
            f"| {headers[4].ljust(col_widths['date'])} |"
        )

        lines = [sep, header_str, sep]
        for r in rows:
            amt_formatted = f"${float(r['amount']):.2f}"
            row_str = (
                f"| {str(r['id']).ljust(col_widths['id'])} "
                f"| {str(r['title']).ljust(col_widths['title'])} "
                f"| {amt_formatted.rjust(col_widths['amount'])} "
                f"| {str(r['category']).ljust(col_widths['category'])} "
                f"| {str(r['date']).ljust(col_widths['date'])} |"
            )
            lines.append(row_str)
        lines.append(sep)
        return "\n".join(lines)


def format_category_table(breakdown: List[Dict[str, Any]]) -> str:
    """
    Renders a formatted ASCII table for category breakdown statistics.
    """
    if not breakdown:
        return "  No category data recorded."

    headers = ["Category", "Entries", "Total Spent", "% of Total"]
    table_data = [
        [
            b["category"],
            str(b["count"]),
            f"${float(b['total']):.2f}",
            f"{float(b.get('percentage', 0.0)):.1f}%"
        ]
        for b in breakdown
    ]

    try:
        from tabulate import tabulate
        return tabulate(table_data, headers=headers, tablefmt="grid")
    except ImportError:
        col_w = {
            "cat": max(len("Category"), max(len(r[0]) for r in table_data)),
            "cnt": max(len("Entries"), max(len(r[1]) for r in table_data)),
            "tot": max(len("Total Spent"), max(len(r[2]) for r in table_data)),
            "pct": max(len("% of Total"), max(len(r[3]) for r in table_data)),
        }
        sep = "+-" + "-+-".join("-" * col_w[k] for k in ["cat", "cnt", "tot", "pct"]) + "-+"
        header_line = (
            f"| {headers[0].ljust(col_w['cat'])} "
            f"| {headers[1].ljust(col_w['cnt'])} "
            f"| {headers[2].ljust(col_w['tot'])} "
            f"| {headers[3].ljust(col_w['pct'])} |"
        )
        lines = [sep, header_line, sep]
        for r in table_data:
            lines.append(
                f"| {r[0].ljust(col_w['cat'])} "
                f"| {r[1].rjust(col_w['cnt'])} "
                f"| {r[2].rjust(col_w['tot'])} "
                f"| {r[3].rjust(col_w['pct'])} |"
            )
        lines.append(sep)
        return "\n".join(lines)


def print_banner():
    banner = """
======================================================================
               PERSONAL EXPENSE TRACKER (CLI)
                Powered by Python & SQLite
======================================================================
"""
    print(banner)


def print_menu():
    print("\n---------------------- MAIN MENU ----------------------")
    print("  1. Add New Expense")
    print("  2. View All Expenses")
    print("  3. Search by Category")
    print("  4. Calculate Total Expenses")
    print("  5. Monthly Expense Summary")
    print("  6. Delete Expense")
    print("  7. Export to CSV")
    print("  8. Exit")
    print("-------------------------------------------------------")


def print_categories(manager: ExpenseManager):
    print("\nAvailable Categories:")
    for idx, cat in enumerate(manager.CATEGORIES, 1):
        print(f"  {idx:>2}. {cat}")


def handle_add_expense(manager: ExpenseManager):
    print("\n--- [1] Add New Expense ---")
    
    # 1. Title input & validation
    title = input("Enter expense title: ").strip()
    try:
        manager.validate_title(title)
    except ValueError as err:
        print(f"[ERROR] {err}")
        return

    # 2. Amount input & validation
    amount_str = input("Enter amount ($): ").strip()
    try:
        manager.validate_amount(amount_str)
    except ValueError as err:
        print(f"[ERROR] {err}")
        return

    # 3. Category selection & validation
    print_categories(manager)
    cat_input = input("Select category (name or 1-10): ").strip()
    try:
        category = manager.validate_category(cat_input)
    except ValueError as err:
        print(f"[ERROR] {err}")
        return

    # 4. Date input & validation
    date_input = input("Enter date (YYYY-MM-DD) [Press Enter for today]: ").strip()
    try:
        date_val = manager.validate_date(date_input)
    except ValueError as err:
        print(f"[ERROR] {err}")
        return

    # Store record in SQLite
    try:
        record = manager.add_expense(title, amount_str, category, date_val)
        print("\n[SUCCESS] Expense added successfully!")
        print(f"  ID:       {record['id']}")
        print(f"  Title:    {record['title']}")
        print(f"  Amount:   ${record['amount']:.2f}")
        print(f"  Category: {record['category']}")
        print(f"  Date:     {record['date']}")
    except ValueError as err:
        print(f"[ERROR] Failed to save expense: {err}")


def handle_view_expenses(manager: ExpenseManager):
    print("\n--- [2] View All Expenses ---")
    expenses = manager.list_expenses()
    if not expenses:
        print("\nNo expenses found. Use 'Add New Expense' to record your first expense.")
        return

    print("\n" + format_table(expenses))
    total_spent = sum(float(r["amount"]) for r in expenses)
    print(f"\nTotal Records: {len(expenses)} | Total Spent: ${total_spent:,.2f}")


def handle_search_by_category(manager: ExpenseManager, category_arg: Optional[str] = None):
    print("\n--- [3] Search by Category ---")
    if category_arg:
        cat_input = category_arg
    else:
        print_categories(manager)
        cat_input = input("Enter category to search (name or 1-10): ").strip()

    try:
        result = manager.search_by_category(cat_input)
    except ValueError as err:
        print(f"[ERROR] {err}")
        return

    category_name = result["category"]
    expenses = result["expenses"]

    print(f"\nSearch Results for Category: '{category_name}'")
    if not expenses:
        print(f"No expenses found under category '{category_name}'.")
        return

    print("\n" + format_table(expenses))
    print(f"\nCategory Summary for '{category_name}':")
    print(f"  Total Spending:    ${result['total_spent']:,.2f}")
    print(f"  Transaction Count: {result['count']}")
    print(f"  Average Expense:   ${result['average_expense']:,.2f}")


def handle_calculate_total_expenses(manager: ExpenseManager):
    print("\n--- [4] Calculate Total Expenses ---")
    stats = manager.calculate_total_expenses()

    total_spent = stats["total_spent"]
    count = stats["transaction_count"]
    avg_spent = stats["average_expense"]
    high = stats["highest_expense"]

    print("\n=======================================================")
    print("               OVERALL EXPENSES SUMMARY")
    print("=======================================================")
    print(f"  Total Spending:       ${total_spent:,.2f}")
    print(f"  Transaction Count:    {count}")
    print(f"  Average Expense:      ${avg_spent:,.2f}")

    if high:
        print(f"  Highest Expense:      '{high['title']}' - ${float(high['amount']):,.2f} ({high['category']} on {high['date']})")
    else:
        print("  Highest Expense:      None")

    print("\nCategory-Wise Spending:")
    print(format_category_table(stats["category_spending"]))


def handle_monthly_summary(manager: ExpenseManager, month_arg: Optional[str] = None):
    print("\n--- [5] Monthly Expense Summary ---")

    if month_arg is not None:
        month_input = month_arg
    else:
        available = manager.get_available_months()
        if available:
            print(f"Recorded months in database: {', '.join(available)}")
        current_m = datetime.now().strftime("%Y-%m")
        month_input = input(f"Enter month (YYYY-MM) [Press Enter for current month: {current_m}]: ").strip()

    try:
        summary = manager.get_monthly_summary(month_input)
    except ValueError as err:
        print(f"[ERROR] {err}")
        return

    month_label = summary["month_name"]
    total_spent = summary["total_spent"]
    count = summary["transaction_count"]
    avg_spent = summary["average_expense"]
    high = summary["highest_expense"]
    expenses = summary["expenses"]

    print("\n=======================================================")
    print(f"         MONTHLY EXPENSE SUMMARY: {month_label.upper()}")
    print("=======================================================")
    print(f"  Target Month:         {summary['month']} ({month_label})")
    print(f"  Total Spending:       ${total_spent:,.2f}")
    print(f"  Transaction Count:    {count}")
    print(f"  Average Expense:      ${avg_spent:,.2f}")

    if high:
        print(f"  Highest Monthly Exp:  '{high['title']}' - ${float(high['amount']):,.2f} ({high['category']} on {high['date']})")
    else:
        print("  Highest Monthly Exp:  None")

    print(f"\nCategory-Wise Spending for {month_label}:")
    print(format_category_table(summary["category_spending"]))

    if expenses:
        print(f"\nTransactions in {month_label}:")
        print(format_table(expenses))
    else:
        print(f"\n(No transactions recorded for {month_label}.)")


def handle_delete_expense(manager: ExpenseManager):
    print("\n--- [6] Delete Expense ---")
    id_str = input("Enter Expense ID to delete: ").strip()
    try:
        expense_id = int(id_str)
    except (ValueError, TypeError):
        print("[ERROR] Please enter a valid numeric ID.")
        return

    existing = manager.get_expense(expense_id)
    if not existing:
        print(f"[ERROR] No expense found with ID {expense_id}.")
        return

    # Display expense details
    print(f"\nExpense Details:")
    print(f"  ID:       {existing['id']}")
    print(f"  Title:    {existing['title']}")
    print(f"  Amount:   ${float(existing['amount']):.2f}")
    print(f"  Category: {existing['category']}")
    print(f"  Date:     {existing['date']}")

    # Ask for confirmation before deleting
    confirm = input("\nAre you sure you want to delete this expense? (y/N): ").strip().lower()
    if confirm in ("y", "yes"):
        if manager.delete_expense(expense_id):
            print(f"\n[SUCCESS] Expense ID {expense_id} deleted successfully.")
        else:
            print(f"\n[ERROR] Could not delete expense ID {expense_id}.")
    else:
        print("\n[INFO] Deletion canceled.")


def handle_export_csv(manager: ExpenseManager, filepath_arg: Optional[str] = None):
    print("\n--- [7] Export to CSV ---")
    default_filename = "expenses_export.csv"
    if filepath_arg:
        filename = filepath_arg.strip()
    else:
        user_input = input(f"Enter output CSV filename [Press Enter for default: {default_filename}]: ").strip()
        filename = user_input if user_input else default_filename

    try:
        count = manager.export_to_csv(filename)
        print(f"\n[SUCCESS] Successfully exported {count} expense records to '{filename}'.")
    except Exception as err:
        print(f"\n[ERROR] Failed to export CSV: {err}")


def interactive_mode(manager: ExpenseManager):
    """
    Main interactive loop for the CLI.
    Runs continuously until Exit (Option 8) is selected.
    """
    print_banner()
    while True:
        try:
            print_menu()
            choice = input("Select an option (1-8): ").strip()
            if choice == "1":
                handle_add_expense(manager)
            elif choice == "2":
                handle_view_expenses(manager)
            elif choice == "3":
                handle_search_by_category(manager)
            elif choice == "4":
                handle_calculate_total_expenses(manager)
            elif choice == "5":
                handle_monthly_summary(manager)
            elif choice == "6":
                handle_delete_expense(manager)
            elif choice == "7":
                handle_export_csv(manager)
            elif choice == "8":
                print("\nThank you for using Personal Expense Tracker. Goodbye!\n")
                break
            else:
                print("\n[WARNING] Invalid selection. Please enter a number between 1 and 8.")
        except (KeyboardInterrupt, EOFError):
            print("\n\nOperation interrupted by user. Exiting Personal Expense Tracker.\n")
            break
        except Exception as err:
            print(f"\n[UNEXPECTED ERROR] {err}")


def main():
    parser = argparse.ArgumentParser(description="Personal Expense Tracker CLI")
    parser.add_argument("--init-db", action="store_true", help="Initialize the SQLite database schema")
    parser.add_argument("--view", "--list", action="store_true", dest="view", help="Display all expenses")
    parser.add_argument("--add", nargs="+", metavar="PARAM",
                        help="Add an expense: --add <title> <amount> <category> [date]")
    parser.add_argument("--delete", type=int, metavar="ID", help="Delete an expense by ID")
    parser.add_argument("--yes", "-y", action="store_true", help="Skip confirmation prompt for CLI delete")
    parser.add_argument("--category", "--search", type=str, metavar="CATEGORY",
                        help="Search expenses by category")
    parser.add_argument("--total", action="store_true", help="Calculate and display total spending statistics")
    parser.add_argument("--monthly", nargs="?", const="", metavar="YYYY-MM",
                        help="Monthly expense summary (default: current month)")
    parser.add_argument("--export", nargs="?", const="expenses_export.csv", metavar="FILE",
                        help="Export expenses to CSV file")
    args = parser.parse_args()

    manager = ExpenseManager()

    if args.init_db:
        print(f"Database initialized successfully at: {manager.db_path}")
        return

    if args.add:
        if len(args.add) < 3:
            print("[ERROR] Please provide at least Title, Amount, and Category.")
            print("Usage: python main.py --add <title> <amount> <category> [date]")
            return
        title = args.add[0]
        amount = args.add[1]
        category = args.add[2]
        date = args.add[3] if len(args.add) > 3 else None
        try:
            record = manager.add_expense(title, amount, category, date)
            print("[SUCCESS] Expense added successfully!")
            print(f"  ID:       {record['id']}")
            print(f"  Title:    {record['title']}")
            print(f"  Amount:   ${record['amount']:.2f}")
            print(f"  Category: {record['category']}")
            print(f"  Date:     {record['date']}")
        except ValueError as err:
            print(f"[ERROR] {err}")
        return

    if args.view:
        expenses = manager.list_expenses()
        print(format_table(expenses))
        return

    if args.delete is not None:
        expense_id = args.delete
        existing = manager.get_expense(expense_id)
        if not existing:
            print(f"[ERROR] No expense found with ID {expense_id}.")
            return
        if not args.yes:
            print(f"Expense Details:")
            print(f"  ID:       {existing['id']}")
            print(f"  Title:    {existing['title']}")
            print(f"  Amount:   ${float(existing['amount']):.2f}")
            print(f"  Category: {existing['category']}")
            print(f"  Date:     {existing['date']}")
            confirm = input("Are you sure you want to delete this expense? (y/N): ").strip().lower()
            if confirm not in ("y", "yes"):
                print("[INFO] Deletion canceled.")
                return
        if manager.delete_expense(expense_id):
            print(f"[SUCCESS] Expense ID {expense_id} deleted successfully.")
        else:
            print(f"[ERROR] Could not delete expense ID {expense_id}.")
        return

    if args.category:
        handle_search_by_category(manager, category_arg=args.category)
        return

    if args.total:
        handle_calculate_total_expenses(manager)
        return

    if args.monthly is not None:
        handle_monthly_summary(manager, month_arg=args.monthly if args.monthly != "" else None)
        return

    if args.export:
        handle_export_csv(manager, filepath_arg=args.export)
        return

    # Default to interactive CLI loop
    interactive_mode(manager)


if __name__ == "__main__":
    main()
