import os
import sqlite3
import subprocess
import sys
from contextlib import closing
from dataclasses import replace
from datetime import date
from decimal import Decimal, InvalidOperation, localcontext
from pathlib import Path

import pytest

from financial_assistant.models import FinancialGoal, Transaction
from financial_assistant.repository import SQLiteRepository


@pytest.fixture
def repository(tmp_path):
    return SQLiteRepository(tmp_path / "nested" / "financial.db")


def test_goal_crud_retains_fields_and_other_records(repository):
    original = FinancialGoal("Emergency fund", "1000.125", "12.345", date(2028, 2, 29), 2)
    goal_id = repository.add_goal(original)
    other_id = repository.add_goal(FinancialGoal("Other goal", 1))
    stored = repository.get_goal(goal_id)
    assert stored == replace(original, goal_id=goal_id)
    changed = replace(stored, name="Reached", target_amount="1200.00", saved_amount="1300",
                      deadline=None, priority=1, status="completed")
    assert repository.update_goal(changed) is True
    assert repository.get_goal(goal_id) == changed
    assert repository.get_goal(other_id).name == "Other goal"
    assert repository.delete_goal(goal_id) is True
    assert repository.get_goal(goal_id) is None
    assert repository.delete_goal(goal_id) is False
    assert repository.update_goal(changed) is False
    assert [goal.goal_id for goal in repository.list_goals()] == [other_id]


def test_transaction_crud_preserves_exact_money_and_metadata(repository):
    original = Transaction("income", "999999999999999999999.99", date(2024, 2, 29), "Other", "Salary", True)
    transaction_id = repository.add_transaction(original)
    other_id = repository.add_transaction(Transaction("expense", ".01", date(2024, 3, 1), "Food"))
    stored = repository.get_transaction(transaction_id)
    assert stored == replace(original, transaction_id=transaction_id)
    changed = replace(stored, transaction_type="expense", amount="12.345", transaction_date=date(2025, 1, 1),
                      category="Health", description="", recurring=False)
    assert repository.update_transaction(changed) is True
    assert repository.get_transaction(transaction_id) == changed
    assert repository.get_transaction(other_id).amount == Decimal(".01")
    assert repository.delete_transaction(transaction_id) is True
    assert repository.get_transaction(transaction_id) is None
    assert repository.delete_transaction(transaction_id) is False
    assert repository.update_transaction(changed) is False
    assert [item.transaction_id for item in repository.list_transactions()] == [other_id]


def test_missing_records_and_empty_lists(repository):
    assert repository.get_goal(1) is None
    assert repository.get_transaction(1) is None
    assert repository.delete_goal(1) is False
    assert repository.delete_transaction(1) is False
    assert repository.list_goals() == []
    assert repository.list_transactions("2026-01", "income", "Other") == []


def test_restart_in_new_process_preserves_records_and_initialization_is_idempotent(repository):
    goal_id = repository.add_goal(FinancialGoal("Goal", "100.01"))
    transaction_id = repository.add_transaction(Transaction("expense", "0.01", date(2026, 1, 1), "Food"))
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1] / "src")
    code = """
import sys
from decimal import Decimal
from financial_assistant.repository import SQLiteRepository
repository = SQLiteRepository(sys.argv[1])
assert repository.get_goal(int(sys.argv[2])).target_amount == Decimal('100.01')
assert repository.get_transaction(int(sys.argv[3])).amount == Decimal('0.01')
assert len(repository.list_goals()) == len(repository.list_transactions()) == 1
"""
    subprocess.run([sys.executable, "-B", "-c", code, str(repository.database_path), str(goal_id), str(transaction_id)],
                   env=env, check=True, capture_output=True, text=True)


def test_transaction_filters_combine_and_respect_calendar_boundaries(repository):
    records = [
        ("income", date(2023, 12, 31), "Other"),
        ("income", date(2024, 2, 1), "Other"),
        ("income", date(2024, 2, 29), "Other"),
        ("expense", date(2024, 2, 29), "Food"),
        ("income", date(2024, 3, 1), "Other"),
        ("expense", date(2024, 2, 29), "Other"),
    ]
    ids = [repository.add_transaction(Transaction(kind, 1, day, category)) for kind, day, category in records]
    def selected(*args, **kwargs):
        return [item.transaction_id for item in repository.list_transactions(*args, **kwargs)]
    assert selected("2024-02") == [ids[5], ids[3], ids[2], ids[1]]
    assert selected(transaction_type="expense") == [ids[5], ids[3]]
    assert selected(category="Food") == [ids[3]]
    assert selected("2024-02", "income", "Other") == [ids[2], ids[1]]
    assert selected("2024-03", "expense") == []
    assert selected("0001-01") == []
    assert selected("9999-12") == []
    assert selected("2023-12") == [ids[0]]


@pytest.mark.parametrize("filters", [
    {"month": ""}, {"month": "2024-2"}, {"month": "0000-01"}, {"month": "2024-13"},
    {"month": "2024-00"}, {"month": "2024-02-01"}, {"month": 202402},
    {"month": "2024-02' OR 1=1 --"}, {"transaction_type": ""},
    {"transaction_type": "income' OR 1=1 --"}, {"transaction_type": []},
    {"category": ""}, {"category": "Unknown"}, {"category": []},
])
def test_invalid_filters_are_rejected(repository, filters):
    with pytest.raises(ValueError):
        repository.list_transactions(**filters)


@pytest.mark.parametrize("value", [None, True, 0, -1, "1", 1.5, 2**63, "1 OR 1=1"])
def test_invalid_record_ids_cannot_read_update_or_delete(repository, value):
    for operation in (repository.get_goal, repository.delete_goal,
                      repository.get_transaction, repository.delete_transaction):
        with pytest.raises(ValueError, match="Record ID"):
            operation(value)
    with pytest.raises(ValueError, match="Record ID"):
        repository.update_goal(FinancialGoal("Goal", 1, goal_id=value))
    with pytest.raises(ValueError, match="Record ID"):
        repository.update_transaction(Transaction("income", 1, date(2026, 1, 1), "Other", transaction_id=value))


def test_user_text_is_stored_literally_not_executed(repository):
    text = "Robert'); DROP TABLE goals; --"
    goal_id = repository.add_goal(FinancialGoal(text, 1))
    transaction_id = repository.add_transaction(Transaction("income", 1, date(2026, 1, 1), "Other", text))
    assert repository.get_goal(goal_id).name == text
    assert repository.get_transaction(transaction_id).description == text
    assert repository.update_goal(replace(repository.get_goal(goal_id), name="O'Brien"))
    assert repository.get_goal(goal_id).name == "O'Brien"


@pytest.mark.parametrize("field", ["target_amount", "saved_amount", "amount"])
def test_invalid_mutated_models_cannot_insert_or_overwrite_valid_data(repository, field):
    if field == "amount":
        original = Transaction("income", 1, date(2026, 1, 1), "Other")
        record_id = repository.add_transaction(original)
        stored = repository.get_transaction(record_id)
        add, update, get = repository.add_transaction, repository.update_transaction, repository.get_transaction
    else:
        original = FinancialGoal("Goal", 100)
        record_id = repository.add_goal(original)
        stored = repository.get_goal(record_id)
        add, update, get = repository.add_goal, repository.update_goal, repository.get_goal
    invalid = replace(stored)
    object.__setattr__(invalid, field, Decimal("NaN"))
    with localcontext() as context:
        context.traps[InvalidOperation] = False
        with pytest.raises(ValueError):
            add(invalid)
        with pytest.raises(ValueError):
            update(invalid)
    assert get(record_id) == stored
    assert len(repository.list_goals()) + len(repository.list_transactions()) == 1


def test_priority_outside_sqlite_integer_range_is_rejected_before_write(repository):
    with pytest.raises(ValueError, match="Priority"):
        repository.add_goal(FinancialGoal("Goal", 1, priority=2**63))
    assert repository.list_goals() == []


def test_failed_write_rolls_back_and_connections_close(repository, monkeypatch):
    goal_id = repository.add_goal(FinancialGoal("Original", 1))
    with closing(sqlite3.connect(repository.database_path)) as connection, connection:
        connection.executescript("""
            CREATE TRIGGER fail_goal_update AFTER UPDATE ON goals BEGIN
                INSERT INTO goals (name, target_amount, saved_amount, priority, status)
                VALUES ('Should roll back', '1.00', '0.00', 1, 'active');
                SELECT RAISE(ABORT, 'test failure');
            END;
        """)
    connections = []
    real_connect = sqlite3.connect
    def tracked_connect(*args, **kwargs):
        connection = real_connect(*args, **kwargs)
        connections.append(connection)
        return connection
    monkeypatch.setattr(sqlite3, "connect", tracked_connect)
    with pytest.raises(sqlite3.IntegrityError, match="test failure"):
        repository.update_goal(FinancialGoal("Changed", 2, goal_id=goal_id))
    assert repository.get_goal(goal_id).name == "Original"
    assert len(repository.list_goals()) == 1
    for connection in connections:
        with pytest.raises(sqlite3.ProgrammingError, match="closed"):
            connection.execute("SELECT 1")


def test_relative_database_path_stays_stable_after_chdir(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    repository = SQLiteRepository("local/data.db")
    goal_id = repository.add_goal(FinancialGoal("Goal", 1))
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    monkeypatch.chdir(elsewhere)
    assert repository.get_goal(goal_id).name == "Goal"
    assert not (elsewhere / "local").exists()


def test_in_memory_path_fails_clearly():
    with pytest.raises(ValueError, match="database file"):
        SQLiteRepository(":memory:")


def test_corrupt_stored_recurring_flag_is_not_silently_coerced(repository):
    transaction_id = repository.add_transaction(Transaction("income", 1, date(2026, 1, 1), "Other"))
    with closing(sqlite3.connect(repository.database_path)) as connection, connection:
        connection.execute("UPDATE transactions SET recurring = 2 WHERE id = ?", (transaction_id,))
    with pytest.raises(ValueError, match="recurring"):
        repository.get_transaction(transaction_id)
    with pytest.raises(ValueError, match="recurring"):
        repository.list_transactions()
