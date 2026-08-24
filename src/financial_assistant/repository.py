import sqlite3
from datetime import date
from decimal import Decimal
from pathlib import Path

from .models import FinancialGoal, Transaction


class SQLiteRepository:
    def __init__(self, database_path: str | Path = "data/financial_assistant.db") -> None:
        self.database_path = Path(database_path)
        if str(self.database_path) != ":memory:":
            self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
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

    def add_goal(self, goal: FinancialGoal) -> int:
        with self._connect() as connection:
            cursor = connection.execute(
                "INSERT INTO goals (name, target_amount, saved_amount, deadline, priority, status) VALUES (?, ?, ?, ?, ?, ?)",
                (goal.name, str(goal.target_amount), str(goal.saved_amount), goal.deadline.isoformat() if goal.deadline else None, goal.priority, goal.status),
            )
            return int(cursor.lastrowid)

    def list_goals(self) -> list[FinancialGoal]:
        with self._connect() as connection:
            rows = connection.execute("SELECT * FROM goals ORDER BY status, priority, id").fetchall()
        return [
            FinancialGoal(row["name"], Decimal(row["target_amount"]), Decimal(row["saved_amount"]), date.fromisoformat(row["deadline"]) if row["deadline"] else None, row["priority"], row["status"], row["id"])
            for row in rows
        ]

    def add_transaction(self, transaction: Transaction) -> int:
        with self._connect() as connection:
            cursor = connection.execute(
                "INSERT INTO transactions (transaction_type, amount, transaction_date, category, description, recurring) VALUES (?, ?, ?, ?, ?, ?)",
                (transaction.transaction_type, str(transaction.amount), transaction.transaction_date.isoformat(), transaction.category, transaction.description, int(transaction.recurring)),
            )
            return int(cursor.lastrowid)

    def list_transactions(self, month: str | None = None) -> list[Transaction]:
        query = "SELECT * FROM transactions"
        parameters: tuple[str, ...] = ()
        if month:
            query += " WHERE substr(transaction_date, 1, 7) = ?"
            parameters = (month,)
        query += " ORDER BY transaction_date DESC, id DESC"
        with self._connect() as connection:
            rows = connection.execute(query, parameters).fetchall()
        return [
            Transaction(row["transaction_type"], Decimal(row["amount"]), date.fromisoformat(row["transaction_date"]), row["category"], row["description"], bool(row["recurring"]), row["id"])
            for row in rows
        ]