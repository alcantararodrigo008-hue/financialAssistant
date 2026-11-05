from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from financial_assistant.models import FinancialGoal, Transaction
from financial_assistant.repository import SQLiteRepository


@pytest.mark.parametrize("records,expected,status", [
    ([], ["0.00 EUR", "0.00 EUR", "0.00 EUR", "No income"], "No transactions recorded"),
    ([("income", "100")], ["100.00 EUR", "0.00 EUR", "100.00 EUR", "100.0%"], "No expenses recorded"),
    ([("expense", "25")], ["0.00 EUR", "25.00 EUR", "-25.00 EUR", "No income"], "Monthly deficit: 25.00 EUR"),
    ([("income", "100"), ("expense", "125")], ["100.00 EUR", "125.00 EUR", "-25.00 EUR", "-25.0%"], "Monthly deficit: 25.00 EUR"),
    ([("income", "100"), ("expense", "100")], ["100.00 EUR", "100.00 EUR", "0.00 EUR", "0.0%"], "Balanced month"),
    ([("income", "1000"), ("expense", "1000.01")], ["1000.00 EUR", "1000.01 EUR", "-0.01 EUR", "0.0%"], "Monthly deficit: 0.01 EUR"),
    ([("income", "1000.01"), ("expense", "1000")], ["1000.01 EUR", "1000.00 EUR", "0.01 EUR", "0.0%"], "Monthly surplus: 0.01 EUR"),
    ([("expense", "99999999999999999999999999.99")] * 2,
     ["0.00 EUR", "199999999999999999999999999.98 EUR", "-199999999999999999999999999.98 EUR", "No income"],
     "Monthly deficit: 199999999999999999999999999.98 EUR"),
])
def test_financial_and_goal_edge_cases_render_persist_and_reject_invalid_saves(tmp_path, monkeypatch, records, expected, status):
    path = Path(__file__).resolve().parents[1] / "app.py"
    monkeypatch.chdir(tmp_path)
    repository = SQLiteRepository(tmp_path / "data" / "financial_assistant.db")
    for kind, amount in records:
        repository.add_transaction(Transaction(kind, amount, date(2024, 2, 29), "Other"))
    # Neighboring-month money must not change a zero-income/deficit classification.
    repository.add_transaction(Transaction("income", "999", date(2024, 3, 1), "Other"))
    today = datetime.now(timezone.utc).date()
    for goal in [
        FinancialGoal("No date", 100, 25),
        FinancialGoal("Past deadline", 100, 25, today - timedelta(days=2)),
        FinancialGoal("Stored complete", 100, 25, today - timedelta(days=2), status="completed"),
        FinancialGoal("Already reached", 100, 125, today - timedelta(days=2)),
    ]:
        repository.add_goal(goal)
    original_goals, original_transactions = repository.list_goals(), repository.list_transactions()
    app = AppTest.from_file(str(path), default_timeout=10).run()
    app.date_input(key="dashboard_month").set_value(date(2024, 2, 1)).run()

    def assert_edge_states(rendered):
        assert not rendered.exception
        assert [item.value for item in rendered.metric] == expected
        messages = [item.value for item in rendered.info] + [item.value for item in rendered.warning]
        assert any(status in message for message in messages)
        financial_warnings = [item.value for item in rendered.warning if "Monthly deficit:" in item.value]
        assert bool(financial_warnings) == status.startswith("Monthly deficit:")
        assert any("Overdue goal" in item.value for item in rendered.warning)
        assert len([item for item in rendered.warning if "Overdue goal" in item.value]) == 1
        assert any("No deadline" in item.value for item in rendered.info)
        assert any("Marked completed" in item.value for item in rendered.info)
        assert any("Goal reached" in item.value for item in rendered.success)
        assert not any("Required monthly savings" in item.value for item in rendered.markdown)
        assert repository.list_goals() == original_goals
        assert repository.list_transactions() == original_transactions

    assert_edge_states(app)
    next(item for item in app.text_input if item.label == "Amount (EUR)").set_value("nan")
    next(item for item in app.button if item.label == "Save transaction").click().run()
    assert app.error
    assert not any("Transaction saved" in item.value for item in app.success)
    assert_edge_states(app)
    reopened = AppTest.from_file(str(path), default_timeout=10).run()
    reopened.date_input(key="dashboard_month").set_value(date(2024, 2, 1)).run()
    assert_edge_states(reopened)
