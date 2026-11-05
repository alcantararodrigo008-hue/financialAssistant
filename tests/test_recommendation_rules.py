"""Rule contracts: financial evidence, counterexamples, and read-only guidance."""

from dataclasses import replace
from datetime import date
from decimal import Decimal, InvalidOperation, localcontext
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from financial_assistant.guidance_config import GuidanceConfig
from financial_assistant.models import FinancialGoal, Transaction
from financial_assistant.recommendations import recommendations
from financial_assistant.repository import SQLiteRepository

DAY = date(2024, 1, 31)
FUND = FinancialGoal("Emergency fund", 100)


def transaction(kind, amount, category="Other"):
    return Transaction(kind, amount, DAY, category)


def rule(records, code, goals=(FUND,), **kwargs):
    return [item.explanation for item in recommendations(records, goals, as_of=DAY, **kwargs) if item.code == code]


@pytest.mark.parametrize("income,expense,shortfall", [
    ("100", "125", "25.00"), ("1000", "1000.01", "0.01"),
    (None, "0.01", "0.01"), ("100", "100", None), ("125", "100", None),
])
def test_deficit_evidence_and_nondeficit_counterexamples(income, expense, shortfall):
    records = [transaction("expense", expense)]
    if income is not None:
        records.append(transaction("income", income))
    messages = rule(records, "deficit")
    if shortfall is None:
        assert messages == []
    else:
        assert len(messages) == 1
        assert f"exceed income by {shortfall} EUR this month" in messages[0]
        assert "Review missing income, bills and timing" in messages[0]
        assert "protect basic needs" in messages[0]
        assert rule(records, "low_savings") == []


def test_low_savings_explains_evidence_and_nonpersonal_threshold():
    records = [transaction("income", "1000"), transaction("expense", "950")]
    message, = rule(records, "low_savings")
    assert "net savings are 50.00 EUR against income of 1000.00 EUR" in message
    assert "below the configured 10% review threshold" in message
    assert "after essential costs" in message
    assert "not a personal requirement" in message
    assert rule(records, "low_savings", config=GuidanceConfig("5", "40")) == []
    assert rule([transaction("income", "1000")], "low_savings") == []


def test_category_aggregation_ignores_income_and_explains_share_not_history():
    records = [transaction("expense", "12", "Food"), transaction("expense", "18", "Food"),
               transaction("expense", "50", "Other"), transaction("income", "9999", "Food")]
    assert not any(message.startswith("Food ") for message in rule(records, "category_share"))
    messages = rule(records, "category_share", config=GuidanceConfig("10", "37"))
    food, other = messages
    assert "Food accounts for 30.00 EUR of 80.00 EUR recorded expenses" in food
    assert "configured 37% category-share threshold" in food
    assert "Other accounts for 50.00 EUR of 80.00 EUR" in other
    for message in messages:
        assert "not evidence of unusual historical spending" in message
        assert "do not automatically cut basic needs" in message
    assert rule([transaction("income", "9999", "Food")], "category_share") == []


@pytest.mark.parametrize("deadline,required", [
    (date(2024, 2, 29), "100.00"),  # Jan 31 anniversary clamps to leap day.
    (date(2024, 3, 1), "50.00"),  # Partial second month counts as a full month.
    (date(2024, 4, 30), "33.34"),  # Cent ceiling, not a rounded-down requirement.
])
def test_goal_capacity_explanation_uses_remaining_savings_and_calendar_months(deadline, required):
    goal = FinancialGoal("Trip", "125", "25", deadline)
    records = [transaction("income", "20"), transaction("expense", "10")]
    message, = rule(records, "goal_capacity", goals=[FUND, goal])
    assert f"Goal 'Trip' needs approximately {required} EUR per month" in message
    assert "recorded nonnegative surplus is 10.00 EUR" in message
    for explanation in ("only if affordable", "extending the deadline", "revising the target",
                        "One month is not a forecast", "goals compete", "no money is automatically allocated"):
        assert explanation in message
    assert rule([transaction("income", required)], "goal_capacity", goals=[FUND, goal]) == []


@pytest.mark.parametrize("deadline", [date(2024, 1, 30), DAY])
def test_past_and_today_deadlines_explain_remaining_amount_and_alternatives(deadline):
    goal = FinancialGoal("Trip", "125", "25", deadline)
    message, = rule([], "goal_deadline", goals=[FUND, goal])
    assert "100.00 EUR remaining" in message
    assert deadline.isoformat() in message
    assert "later deadline or revise the target" in message
    assert "no future saving period" in message
    assert rule([], "goal_capacity", goals=[FUND, goal]) == []


@pytest.mark.parametrize("changes", [
    {"status": "completed"}, {"saved_amount": "125"}, {"saved_amount": "150"}, {"deadline": None},
])
def test_finished_or_undated_goals_do_not_claim_unreachable_deadlines(changes):
    goal = replace(FinancialGoal("Trip", "125", "25", DAY), **changes)
    assert recommendations([], [FUND, goal], as_of=DAY) == ()


@pytest.mark.parametrize("name,status,exists", [
    ("Emergency fund", "active", True), ("  EMERGENCY\t fund  ", "active", True),
    ("Emergency fund", "completed", True), ("Emergency funds", "active", False),
    ("Emergency fund holiday", "active", False), ("Holiday", "active", False),
])
def test_emergency_fund_name_contract_and_optional_explanation(name, status, exists):
    messages = rule([], "emergency_fund", goals=[FinancialGoal(name, 100, status=status)])
    if exists:
        assert messages == []
    else:
        message, = messages
        for explanation in ("No goal named 'Emergency fund'", "If useful and affordable after basic needs",
                            "outside this app is not detected", "no investment or fixed target"):
            assert explanation in message


def test_missing_data_does_not_invent_income_expenses_or_future_capacity():
    future = FinancialGoal("Trip", 100, deadline=date(2024, 2, 29))
    assert recommendations([], [FUND, future], as_of=DAY) == ()
    missing = recommendations([], [], as_of=DAY)
    assert [item.code for item in missing] == ["emergency_fund"]
    assert "No goal named 'Emergency fund'" in missing[0].explanation


def test_guidance_is_stable_after_reopening_and_invalid_inputs_cannot_change_data(tmp_path):
    path = tmp_path / "records.db"
    repo = SQLiteRepository(path)
    for item in [transaction("income", "100"), transaction("expense", "60", "Food"),
                 transaction("expense", "65", "Other")]:
        repo.add_transaction(item)
    repo.add_goal(FinancialGoal("Trip", "200", "25", date(2024, 2, 29)))
    before = repo.list_transactions(), repo.list_goals()
    snapshot = path.read_bytes()
    expected = recommendations(*before, as_of=DAY)
    assert {item.code for item in expected} == {"deficit", "category_share", "goal_capacity", "emergency_fund"}
    reopened = SQLiteRepository(path)
    assert recommendations(reversed(reopened.list_transactions()), reopened.list_goals(), as_of=DAY) == expected
    invalid = replace(before[0][0])
    object.__setattr__(invalid, "amount", Decimal("NaN"))
    with localcontext() as context:
        context.traps[InvalidOperation] = False
        with pytest.raises(ValueError, match="Transaction amount"):
            recommendations([invalid], before[1], as_of=DAY)
    assert (reopened.list_transactions(), reopened.list_goals()) == before
    assert path.read_bytes() == snapshot


def test_actual_saves_and_confirmed_deletion_refresh_guidance_after_reopening(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    app_path = str(Path(__file__).resolve().parents[1] / "app.py")
    repo = SQLiteRepository()
    app = AppTest.from_file(app_path, default_timeout=15).run()
    app.date_input(key="dashboard_month").set_value(DAY).run()
    for label, value in [("Goal name", "Emergency fund"), ("Target amount (EUR)", "100"), ("Current savings (EUR)", "0")]:
        next(item for item in app.text_input if item.label == label).set_value(value)
    next(item for item in app.button if item.label == "Save goal").click().run()
    assert not any("No goal named 'Emergency fund'" in item.value for item in app.text)
    next(item for item in app.selectbox if item.label == "Type").set_value("expense")
    next(item for item in app.text_input if item.label == "Amount (EUR)").set_value("25.01")
    next(item for item in app.date_input if item.label == "Date").set_value(DAY)
    next(item for item in app.button if item.label == "Save transaction").click().run()
    assert not app.exception
    assert any("exceed income by 25.01 EUR" in item.value for item in app.text)
    record, = repo.list_transactions()
    app.run()
    assert repo.list_transactions() == [record]
    app.selectbox(key="transaction_to_delete").set_value(record.transaction_id).run()
    next(item for item in app.button if item.label == "Delete transaction").click().run()
    assert repo.list_transactions() == [record]
    assert any("exceed income by 25.01 EUR" in item.value for item in app.text)
    app.button(key="confirm_deletion").click().run()
    assert not app.exception
    assert repo.list_transactions() == []
    assert any("No guidance rules triggered" in item.value for item in app.info)
    reopened = AppTest.from_file(app_path, default_timeout=15).run()
    reopened.date_input(key="dashboard_month").set_value(DAY).run()
    assert not reopened.exception
    assert any("No guidance rules triggered" in item.value for item in reopened.info)
    assert len(repo.list_goals()) == 1
    assert repo.list_goals()[0].saved_amount == Decimal("0.00")
