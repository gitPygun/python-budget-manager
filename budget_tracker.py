import sqlite3
from datetime import date

DATABASE = "budget.db"


def connect_db():
    """Connect to the budget database and create the table."""
    connection = sqlite3.connect(DATABASE)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_type TEXT NOT NULL,
            amount_cents INTEGER NOT NULL,
            category TEXT NOT NULL,
            description TEXT NOT NULL,
            transaction_date TEXT NOT NULL
        )
    """)

    return connection


def get_amount():
    """Get a valid positive money amount in dollars."""
    while True:
        value = input("Enter amount ($): ").strip()

        try:
            dollars, dot, cents = value.partition(".")

            if not dollars.isdigit():
                raise ValueError

            if dot and (
                not cents.isdigit() or len(cents) > 2
            ):
                raise ValueError

            amount_cents = int(dollars) * 100

            if dot:
                amount_cents += int(cents.ljust(2, "0"))

            if amount_cents <= 0:
                raise ValueError

            return amount_cents

        except ValueError:
            print("Enter a positive amount, such as 25 or 25.50.")


def add_transaction(connection, transaction_type):
    """Add an income or expense transaction."""
    amount_cents = get_amount()

    category = input("Enter category: ").strip()
    description = input("Enter description: ").strip()

    if not category or not description:
        print("Category and description cannot be empty.")
        return

    connection.execute("""
        INSERT INTO transactions
        (transaction_type, amount_cents, category,
         description, transaction_date)
        VALUES (?, ?, ?, ?, ?)
    """, (
        transaction_type,
        amount_cents,
        category,
        description,
        date.today().isoformat()
    ))

    connection.commit()
    print(f"{transaction_type.title()} recorded successfully!")


def view_transactions(connection):
    """Display all recorded transactions."""
    rows = connection.execute("""
        SELECT id, transaction_type, amount_cents,
               category, description, transaction_date
        FROM transactions
        ORDER BY id DESC
    """).fetchall()

    if not rows:
        print("\nNo transactions found.")
        return

    print("\n--- Transaction History ---")

    for row in rows:
        transaction_id, kind, cents, category, description, day = row
        amount = cents / 100

        print(
            f"ID: {transaction_id} | {day} | "
            f"{kind.title()} | ${amount:.2f} | "
            f"{category} | {description}"
        )


def show_summary(connection):
    """Calculate income, expenses, and balance."""
    rows = connection.execute("""
        SELECT transaction_type, SUM(amount_cents)
        FROM transactions
        GROUP BY transaction_type
    """).fetchall()

    totals = {"income": 0, "expense": 0}

    for kind, amount in rows:
        totals[kind] = amount or 0

    income = totals["income"]
    expenses = totals["expense"]
    balance = income - expenses

    print("\n--- Budget Summary ---")
    print(f"Total income:   ${income / 100:.2f}")
    print(f"Total expenses: ${expenses / 100:.2f}")
    print(f"Balance:        ${balance / 100:.2f}")


def delete_transaction(connection):
    """Delete a transaction using its ID."""
    view_transactions(connection)

    transaction_id = input(
        "\nEnter transaction ID to delete: "
    ).strip()

    if not transaction_id.isdigit():
        print("Please enter a valid transaction ID.")
        return

    cursor = connection.execute(
        "DELETE FROM transactions WHERE id = ?",
        (int(transaction_id),)
    )

    connection.commit()

    if cursor.rowcount:
        print("Transaction deleted successfully.")
    else:
        print("Transaction ID not found.")


def main():
    connection = connect_db()

    try:
        while True:
            print("\n==========================")
            print("   PERSONAL BUDGET TRACKER")
            print("==========================")
            print("1. Add Income")
            print("2. Add Expense")
            print("3. View Transactions")
            print("4. View Budget Summary")
            print("5. Delete Transaction")
            print("6. Exit")

            choice = input("\nChoose an option: ").strip()

            if choice == "1":
                add_transaction(connection, "income")
            elif choice == "2":
                add_transaction(connection, "expense")
            elif choice == "3":
                view_transactions(connection)
            elif choice == "4":
                show_summary(connection)
            elif choice == "5":
                delete_transaction(connection)
            elif choice == "6":
                print("Thank you for using Budget Tracker!")
                break
            else:
                print("Invalid choice. Select 1 through 6.")

    finally:
        connection.close()


if __name__ == "__main__":
    main()
