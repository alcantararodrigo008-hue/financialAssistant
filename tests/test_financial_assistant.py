from datetime import date, datetime, timezone
from decimal import Decimal

import pytest

from src.financial_assistant.models import FinancialGoal, Transaction
from src.financial_assistant.repository import SQLiteRepository


def test_models_reject_non_positive_amounts():
    with pytest.raises(ValueError):
        FinancialGoal("Viaje", Decimal(0))
    with pytest.raises(ValueError):
        Transaction("expense", Decimal(-1), datetime.now(timezone.utc).date(), "Ocio")


def test_repository_round_trips_goal_and_transaction(tmp_path):
    repository = SQLiteRepository(tmp_path / "test.db")
    goal_id = repository.add_goal(FinancialGoal("Fondo", Decimal(1000)))
    transaction_id = repository.add_transaction(Transaction("income", Decimal(1500), date(2026, 8, 10), "Other"))

    assert repository.list_goals()[0].goal_id == goal_id
    assert repository.list_transactions("2026-08")[0].transaction_id == transaction_id
    assert repository.list_transactions("2026-07") == []


def test_goal_progress_is_capped_at_one():
    goal = FinancialGoal("Fondo", Decimal(100), Decimal(125))

    assert goal.progress == 1.0