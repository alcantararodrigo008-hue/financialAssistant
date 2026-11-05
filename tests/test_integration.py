"""Isolated user journeys joining models, SQLite, dashboard services and Streamlit."""

from dataclasses import replace
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from financial_assistant.goal_planning import required_monthly_savings
from financial_assistant.models import FinancialGoal, Transaction
from financial_assistant.monthly_summary import calculate_monthly_summary
from financial_assistant.recommendations import recommendations
from financial_assistant.repository import SQLiteRepository
from financial_assistant.visualizations import (
    daily_trends_spec,
    expense_distribution_spec,
)


@pytest.mark.parametrize("income,food,other,net,rate,codes", [
    ("1000.00", "300.00", "200.00", "500.00", "50.0", {"category_share", "emergency_fund"}),
    ("1000.00", "588.00", "392.00", "20.00", "2.0",
     {"low_savings", "category_share", "goal_capacity", "emergency_fund"}),
    ("100.00", "75.00", "50.00", "-25.00", "-25.0",
     {"deficit", "category_share", "goal_capacity", "emergency_fund"}),
    (None, "15.00", "10.00", "-25.00", None,
     {"deficit", "category_share", "goal_capacity", "emergency_fund"}),
    ("100.00", "60.00", "40.00", "0.00", "0.0",
     {"low_savings", "category_share", "goal_capacity", "emergency_fund"}),
    (None, None, None, "0.00", None, {"emergency_fund"}),
], ids=["surplus", "low-savings", "deficit", "no-income", "balanced", "missing-data"])
def test_persisted_goal_to_dashboard_journey(tmp_path, income, food, other, net, rate, codes):
    path = tmp_path / "journey" / "data.db"
    repo = SQLiteRepository(path)
    # A separate database acts as a sentinel for accidental cross-database reads/writes.
    foreign_path = tmp_path / "another-user" / "data.db"
    foreign = SQLiteRepository(foreign_path)
    foreign.add_goal(FinancialGoal("Unrelated", "99999"))
    foreign_snapshot = foreign_path.read_bytes()

    as_of = date(2024, 1, 31)
    goal_id = repo.add_goal(FinancialGoal("Trip", "125", "25", date(2024, 4, 30)))
    selected = []
    if income is not None:
        selected.append(Transaction("income", income, date(2024, 1, 1), "Other", "salary", True))
    if food is not None:
        selected.extend([Transaction("expense", food, as_of, "Food", "food"),
                         Transaction("expense", other, as_of, "Other", "bills")])
    for item in selected:
        repo.add_transaction(item)
    # Neither neighboring-month nor same-month/different-year data may leak into totals.
    repo.add_transaction(Transaction("income", "9999", date(2024, 2, 1), "Other"))
    repo.add_transaction(Transaction("expense", "9999", date(2023, 1, 31), "Food"))
    original = repo.list_transactions(), repo.list_goals()
    snapshot = path.read_bytes()

    def verify(reopened):
        records = reopened.list_transactions("2024-01")
        assert len(records) == len(selected)
        assert {(item.transaction_type, item.amount, item.transaction_date, item.category,
                 item.description, item.recurring) for item in records} == {
            (item.transaction_type, item.amount, item.transaction_date, item.category,
             item.description, item.recurring) for item in selected}
        summary = calculate_monthly_summary(records)
        assert summary.income == Decimal(income or "0")
        assert summary.expenses == Decimal(food or "0") + Decimal(other or "0")
        assert summary.net_savings == Decimal(net)
        assert summary.savings_rate_percent == (Decimal(rate) if rate is not None else None)
        goal = reopened.get_goal(goal_id)
        assert goal == replace(FinancialGoal("Trip", "125", "25", date(2024, 4, 30)), goal_id=goal_id)
        assert goal.progress == pytest.approx(0.2)
        assert required_monthly_savings(goal, as_of) == Decimal("33.34")
        suggestions = recommendations(records, reopened.list_goals(), as_of=as_of)
        assert {item.code for item in suggestions} == codes
        messages = {item.code: item.explanation for item in suggestions}
        assert "outside this app is not detected" in messages["emergency_fund"]
        if "goal_capacity" in codes:
            assert "33.34 EUR per month" in messages["goal_capacity"]
            assert f"surplus is {max(Decimal(net), Decimal(0)):.2f} EUR" in messages["goal_capacity"]
        if "deficit" in codes:
            assert "exceed income by 25.00 EUR" in messages["deficit"]
        if "low_savings" in codes:
            assert f"net savings are {Decimal(net):.2f} EUR" in messages["low_savings"]
        bars, trend = expense_distribution_spec(records), daily_trends_spec(records)
        if food is None:
            assert bars is None and trend is None
        else:
            assert {row["Category"]: row["Cents"] for row in bars["data"]["values"]} == {
                "Food": int(Decimal(food) * 100), "Other": int(Decimal(other) * 100)}
            assert sum(row["Cents"] for row in trend["data"]["values"] if row["Series"] == "Net savings") == int(Decimal(net) * 100)
        assert (reopened.list_transactions(), reopened.list_goals()) == original
        assert path.read_bytes() == snapshot
        return goal

    verify(repo)
    saved = verify(SQLiteRepository(path))
    # Goal balances change only through an explicit goal update, not earned income.
    assert repo.update_goal(replace(saved, saved_amount=Decimal(125)))
    reopened = SQLiteRepository(path)
    reached = reopened.get_goal(goal_id)
    assert reached.progress == 1
    assert required_monthly_savings(reached, as_of) == Decimal("0.00")
    assert "goal_capacity" not in {r.code for r in recommendations(
        reopened.list_transactions("2024-01"), reopened.list_goals(), as_of=as_of)}
    assert reopened.list_transactions() == original[0]
    assert foreign_path.read_bytes() == foreign_snapshot


def test_complete_streamlit_journey_keeps_dashboard_and_storage_consistent(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    path = str(Path(__file__).resolve().parents[1] / "app.py")
    app = AppTest.from_file(path, default_timeout=15).run()
    repo = SQLiteRepository(tmp_path / "data" / "financial_assistant.db")
    app.date_input(key="dashboard_month").set_value(date(2024, 2, 1)).run()
    assert not app.exception
    assert [item.value for item in app.metric] == ["0.00 EUR", "0.00 EUR", "0.00 EUR", "No income"]
    for label, value in [("Goal name", "Trip"), ("Target amount (EUR)", "125"), ("Current savings (EUR)", "25")]:
        next(item for item in app.text_input if item.label == label).set_value(value)
    next(item for item in app.button if item.label == "Save goal").click().run()
    assert any(item.value == "Goal saved." for item in app.success)
    for kind, amount, day, category, description in [
        ("income", "1000.10", date(2024, 2, 1), "Other", "salary"),
        ("expense", "950.09", date(2024, 2, 29), "Food", "food"),
        ("income", "9999", date(2024, 3, 1), "Other", "neighboring month"),
        ("expense", "8888", date(2023, 2, 28), "Food", "prior year"),
    ]:
        next(item for item in app.selectbox if item.label == "Type").set_value(kind)
        next(item for item in app.text_input if item.label == "Amount (EUR)").set_value(amount)
        next(item for item in app.date_input if item.label == "Date").set_value(day)
        next(item for item in app.selectbox if item.label == "Category").set_value(category)
        next(item for item in app.text_input if item.label == "Description (optional)").set_value(description)
        next(item for item in app.button if item.label == "Save transaction").click().run()
        assert not app.exception
        assert any(item.value == "Transaction saved." for item in app.success)
    original = repo.list_transactions(), repo.list_goals()
    assert len(original[0]) == 4 and len(original[1]) == 1
    snapshot = repo.database_path.read_bytes()

    def verify(rendered):
        assert not rendered.exception
        assert [item.value for item in rendered.metric] == ["1000.10 EUR", "950.09 EUR", "50.01 EUR", "5.0%"]
        assert rendered.get("progress")[0].value == 20
        assert any("Saved: 25.00 / 125.00 EUR" in item.value for item in rendered.caption)
        text = [item.value for item in rendered.text]
        assert any("net savings are 50.01 EUR against income of 1000.10 EUR" in t for t in text)
        assert any("Food accounts for 950.09 EUR of 950.09 EUR" in t for t in text)
        assert any("No goal named 'Emergency fund'" in t for t in text)
        assert (repo.list_transactions(), repo.list_goals()) == original
        assert repo.database_path.read_bytes() == snapshot

    app.run()
    verify(app)
    assert app.dataframe[0].value["Description"].tolist() == ["food", "salary"]
    app.selectbox(key="transaction_type_filter").set_value("expense")
    app.selectbox(key="transaction_category_filter").set_value("Food").run()
    verify(app)
    assert app.dataframe[0].value["Description"].tolist() == ["food"]
    # Invalid submissions must not partially change any layer of the existing journey.
    for label, value, submit, field in [
        ("Amount (EUR)", "NaN", "Save transaction", "Transaction amount"),
        ("Target amount (EUR)", "not-money", "Save goal", "Target amount"),
    ]:
        if submit == "Save goal":
            # Fill other required fields explicitly; do not assume form retention.
            next(item for item in app.text_input if item.label == "Goal name").set_value("Rejected goal")
            next(item for item in app.text_input if item.label == "Current savings (EUR)").set_value("25")
        next(item for item in app.text_input if item.label == label).set_value(value)
        next(item for item in app.button if item.label == submit).click().run()
        assert any(field in item.value for item in app.error), (field, [item.value for item in app.error])
        assert not any("saved." in item.value for item in app.success)
        verify(app)
    reopened = AppTest.from_file(path, default_timeout=15).run()
    reopened.date_input(key="dashboard_month").set_value(date(2024, 2, 1)).run()
    verify(reopened)
    assert reopened.dataframe[0].value["Description"].tolist() == ["food", "salary"]
    reopened.date_input(key="dashboard_month").set_value(date(2024, 4, 1)).run()
    assert not reopened.exception
    assert [item.value for item in reopened.metric] == ["0.00 EUR", "0.00 EUR", "0.00 EUR", "No income"]
    assert reopened.get("progress")[0].value == 20
    assert not any("below the configured" in item.value for item in reopened.text)
    reopened.date_input(key="dashboard_month").set_value(date(2024, 2, 1)).run()
    verify(reopened)
