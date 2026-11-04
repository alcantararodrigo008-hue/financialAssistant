from dataclasses import FrozenInstanceError
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation, localcontext

import pytest

from financial_assistant.models import CATEGORIES, FinancialGoal, Transaction


@pytest.mark.parametrize("value", [0, -1, "bad", "NaN", "sNaN", "Infinity", "-Infinity", None, True, [], "0.001", "1e100"])
@pytest.mark.parametrize("kind", ["goal", "transaction"])
def test_invalid_positive_amounts_raise_clear_errors(value, kind):
    with pytest.raises(ValueError, match="amount"):
        if kind == "goal":
            FinancialGoal("Goal", value)
        else:
            Transaction("income", value, date(2026, 1, 1), "Other")


@pytest.mark.parametrize("value", [-1, "-0.001", "NaN", "Infinity", "bad", None, True])
def test_invalid_savings(value):
    with pytest.raises(ValueError, match="Current savings"):
        FinancialGoal("Goal", 100, value)


@pytest.mark.parametrize("value", [None, "", "  ", 123])
def test_invalid_goal_names(value):
    with pytest.raises(ValueError, match="name"):
        FinancialGoal(value, 100)


@pytest.mark.parametrize("value", [0, -1, 1.5, True, "1", None])
def test_invalid_priorities(value):
    with pytest.raises(ValueError, match="Priority"):
        FinancialGoal("Goal", 100, priority=value)


@pytest.mark.parametrize("value", ["2026-02-30", "2026-01-01", datetime(2026, 1, 1, tzinfo=timezone.utc), 123])
def test_dates_must_be_calendar_dates(value):
    with pytest.raises(ValueError, match="Deadline"):
        FinancialGoal("Goal", 100, deadline=value)
    with pytest.raises(ValueError, match="Transaction date"):
        Transaction("income", 1, value, "Other")


def test_transaction_requires_date():
    with pytest.raises(ValueError, match="Transaction date"):
        Transaction("income", 1, None, "Other")


@pytest.mark.parametrize("value", ["unknown", None, [], 123])
def test_invalid_choices(value):
    with pytest.raises(ValueError, match="Goal status"):
        FinancialGoal("Goal", 100, status=value)
    with pytest.raises(ValueError, match="Transaction type"):
        Transaction(value, 1, date(2026, 1, 1), "Other")
    with pytest.raises(ValueError, match="Category"):
        Transaction("income", 1, date(2026, 1, 1), value)


@pytest.mark.parametrize("category", sorted(CATEGORIES))
@pytest.mark.parametrize("kind", ["income", "expense"])
def test_valid_transactions(category, kind):
    transaction = Transaction(kind, "12.345", date(2024, 2, 29), category, "", True)
    assert transaction.amount == Decimal("12.34")
    assert transaction.recurring is True


@pytest.mark.parametrize("status", ["active", "completed"])
def test_valid_goals_and_immutability(status):
    goal = FinancialGoal("Goal", 100.125, "125", date(2020, 1, 1), 6, status)
    assert goal.target_amount == Decimal("100.12")
    assert goal.progress == 1.0
    assert FinancialGoal("No deadline", 1).deadline is None
    with pytest.raises(FrozenInstanceError):
        goal.name = "Changed"


def test_transaction_metadata_validation():
    with pytest.raises(ValueError, match="Description"):
        Transaction("income", 1, date(2026, 1, 1), "Other", description=None)
    with pytest.raises(ValueError, match="Recurring"):
        Transaction("income", 1, date(2026, 1, 1), "Other", recurring=1)


@pytest.mark.parametrize("field,label", [
    ("target_amount", "Target amount"),
    ("saved_amount", "Current savings"),
    ("amount", "Transaction amount"),
])
@pytest.mark.parametrize("value", ["1e100", "bad", "NaN", "Infinity"])
def test_invalid_amounts_never_reach_sqlite_with_invalid_operation_untrapped(tmp_path, field, label, value):
    from financial_assistant.repository import SQLiteRepository

    repository = SQLiteRepository(tmp_path / "test.db")
    with localcontext() as context:
        context.traps[InvalidOperation] = False
        with pytest.raises(ValueError, match=label):
            if field == "amount":
                repository.add_transaction(Transaction("income", value, date(2026, 1, 1), "Other"))
            else:
                fields = {"target_amount": 100, "saved_amount": 0, field: value}
                repository.add_goal(FinancialGoal("Goal", **fields))
        assert context.traps[InvalidOperation] is False

    assert repository.list_goals() == []
    assert repository.list_transactions() == []


def test_valid_amounts_round_trip_with_invalid_operation_untrapped(tmp_path):
    from financial_assistant.repository import SQLiteRepository

    repository = SQLiteRepository(tmp_path / "test.db")
    with localcontext() as context:
        context.traps[InvalidOperation] = False
        goal = FinancialGoal("Goal", "100.125", "12.345")
        transaction = Transaction("income", "12.345", date(2026, 1, 1), "Other")
        repository.add_goal(goal)
        repository.add_transaction(transaction)
        assert repository.list_goals()[0].target_amount == Decimal("100.12")
        assert repository.list_goals()[0].saved_amount == Decimal("12.34")
        assert repository.list_transactions()[0].amount == Decimal("12.34")
        assert context.traps[InvalidOperation] is False
