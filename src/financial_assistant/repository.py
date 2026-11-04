import re
import sqlite3
from contextlib import closing, contextmanager
from dataclasses import replace
from datetime import date
from pathlib import Path

from .models import CATEGORIES, TRANSACTION_TYPES, FinancialGoal, Transaction


class SQLiteRepository:
    """File-backed persistence; each operation commits or rolls back and closes."""

    def __init__(self, database_path: str | Path = "data/financial_assistant.db") -> None:
        if str(database_path) == ":memory:":
            raise ValueError("Use a database file; in-memory databases are not supported.")
        # Keep a stable location even if the caller later changes working directory.
        self.database_path = Path(database_path).resolve()
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    @contextmanager
    def _connection(self):
        with closing(sqlite3.connect(self.database_path)) as connection:
            connection.row_factory = sqlite3.Row
            with connection:
                yield connection

    def _initialize(self) -> None:
        with self._connection() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS goals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    target_amount TEXT NOT NULL,
                    saved_amount TEXT NOT NULL,
                    deadline TEXT,
                    priority INTEGER NOT NULL,
                    status TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    transaction_type TEXT NOT NULL,
                    amount TEXT NOT NULL,
                    transaction_date TEXT NOT NULL,
                    category TEXT NOT NULL,
                    description TEXT NOT NULL,
                    recurring INTEGER NOT NULL
                );
                """
            )

    @staticmethod
    def _record_id(value: int) -> int:
        if type(value) is not int or not 1 <= value <= 2**63 - 1:
            raise ValueError("Record ID must be a positive SQLite integer.")
        return value

    @staticmethod
    def _goal_values(goal: FinancialGoal) -> tuple:
        if not isinstance(goal, FinancialGoal):
            raise ValueError("Expected a FinancialGoal.")  # noqa: TRY004 - domain boundary
        goal = replace(goal)  # Revalidate even if a caller bypassed frozen fields.
        if goal.priority > 2**63 - 1:
            raise ValueError("Priority exceeds the supported SQLite integer range.")
        return (
            goal.name, str(goal.target_amount), str(goal.saved_amount),
            goal.deadline.isoformat() if goal.deadline else None, goal.priority, goal.status,
        )

    @staticmethod
    def _transaction_values(transaction: Transaction) -> tuple:
        if not isinstance(transaction, Transaction):
            raise ValueError("Expected a Transaction.")  # noqa: TRY004 - domain boundary
        transaction = replace(transaction)
        return (
            transaction.transaction_type, str(transaction.amount),
            transaction.transaction_date.isoformat(), transaction.category,
            transaction.description, int(transaction.recurring),
        )

    @staticmethod
    def _goal_from_row(row: sqlite3.Row) -> FinancialGoal:
        return FinancialGoal(
            row["name"], row["target_amount"], row["saved_amount"],
            date.fromisoformat(row["deadline"]) if row["deadline"] is not None else None,
            row["priority"], row["status"], row["id"],
        )

    @staticmethod
    def _transaction_from_row(row: sqlite3.Row) -> Transaction:
        if row["recurring"] not in (0, 1):
            raise ValueError("Stored recurring value must be 0 or 1.")
        return Transaction(
            row["transaction_type"], row["amount"], date.fromisoformat(row["transaction_date"]),
            row["category"], row["description"], bool(row["recurring"]), row["id"],
        )

    def add_goal(self, goal: FinancialGoal) -> int:
        values = self._goal_values(goal)
        with self._connection() as connection:
            cursor = connection.execute(
                "INSERT INTO goals (name, target_amount, saved_amount, deadline, priority, status) VALUES (?, ?, ?, ?, ?, ?)",
                values,
            )
            return int(cursor.lastrowid)

    def get_goal(self, goal_id: int) -> FinancialGoal | None:
        goal_id = self._record_id(goal_id)
        with self._connection() as connection:
            row = connection.execute("SELECT * FROM goals WHERE id = ?", (goal_id,)).fetchone()
        return self._goal_from_row(row) if row is not None else None

    def list_goals(self) -> list[FinancialGoal]:
        with self._connection() as connection:
            rows = connection.execute("SELECT * FROM goals ORDER BY status, priority, id").fetchall()
        return [self._goal_from_row(row) for row in rows]

    def update_goal(self, goal: FinancialGoal) -> bool:
        values = self._goal_values(goal)
        goal_id = self._record_id(goal.goal_id)
        with self._connection() as connection:
            cursor = connection.execute(
                "UPDATE goals SET name = ?, target_amount = ?, saved_amount = ?, deadline = ?, priority = ?, status = ? WHERE id = ?",
                (*values, goal_id),
            )
            return cursor.rowcount == 1

    def delete_goal(self, goal_id: int) -> bool:
        goal_id = self._record_id(goal_id)
        with self._connection() as connection:
            return connection.execute("DELETE FROM goals WHERE id = ?", (goal_id,)).rowcount == 1

    def add_transaction(self, transaction: Transaction) -> int:
        values = self._transaction_values(transaction)
        with self._connection() as connection:
            cursor = connection.execute(
                "INSERT INTO transactions (transaction_type, amount, transaction_date, category, description, recurring) VALUES (?, ?, ?, ?, ?, ?)",
                values,
            )
            return int(cursor.lastrowid)

    def get_transaction(self, transaction_id: int) -> Transaction | None:
        transaction_id = self._record_id(transaction_id)
        with self._connection() as connection:
            row = connection.execute("SELECT * FROM transactions WHERE id = ?", (transaction_id,)).fetchone()
        return self._transaction_from_row(row) if row is not None else None

    def list_transactions(
        self, month: str | None = None, transaction_type: str | None = None,
        category: str | None = None,
    ) -> list[Transaction]:
        conditions = []
        parameters = []
        if month is not None:
            if not isinstance(month, str) or re.fullmatch(r"[0-9]{4}-(0[1-9]|1[0-2])", month) is None or month[:4] == "0000":
                raise ValueError("Month must use YYYY-MM with a year from 0001 to 9999.")
            conditions.append("substr(transaction_date, 1, 7) = ?")
            parameters.append(month)
        for column, value, allowed in (
            ("transaction_type", transaction_type, TRANSACTION_TYPES),
            ("category", category, CATEGORIES),
        ):
            if value is not None:
                if not isinstance(value, str) or value not in allowed:
                    raise ValueError(f"Invalid {column} filter; choose from {', '.join(sorted(allowed))}.")
                # Column names come exclusively from the fixed tuple above.
                conditions.append(f"{column} = ?")
                parameters.append(value)
        query = "SELECT * FROM transactions"
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY transaction_date DESC, id DESC"
        with self._connection() as connection:
            rows = connection.execute(query, parameters).fetchall()
        return [self._transaction_from_row(row) for row in rows]

    def update_transaction(self, transaction: Transaction) -> bool:
        values = self._transaction_values(transaction)
        transaction_id = self._record_id(transaction.transaction_id)
        with self._connection() as connection:
            cursor = connection.execute(
                "UPDATE transactions SET transaction_type = ?, amount = ?, transaction_date = ?, category = ?, description = ?, recurring = ? WHERE id = ?",
                (*values, transaction_id),
            )
            return cursor.rowcount == 1

    def delete_transaction(self, transaction_id: int) -> bool:
        transaction_id = self._record_id(transaction_id)
        with self._connection() as connection:
            return connection.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,)).rowcount == 1
