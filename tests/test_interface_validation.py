from dataclasses import replace
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from financial_assistant.models import FinancialGoal, Transaction
from financial_assistant.repository import SQLiteRepository


@pytest.fixture
def validation_app(tmp_path, monkeypatch):
    path = Path(__file__).resolve().parents[1] / "app.py"
    monkeypatch.chdir(tmp_path)
    return SQLiteRepository(tmp_path / "data" / "financial_assistant.db"), AppTest.from_file(str(path), default_timeout=10)


@pytest.mark.parametrize("label,value,submit,error", [
    ("Amount (EUR)", 0.0, "Save transaction", "greater than zero"),
    ("Amount (EUR)", -1.0, "Save transaction", "greater than zero"),
    ("Amount (EUR)", 0.001, "Save transaction", "after rounding"),
    ("Target amount (EUR)", 0.0, "Save goal", "greater than zero"),
    ("Target amount (EUR)", -1.0, "Save goal", "greater than zero"),
    ("Current savings (EUR)", -1.0, "Save goal", "cannot be negative"),
])
def test_invalid_amounts_show_errors_without_changing_existing_records(validation_app, label, value, submit, error):
    repository, app = validation_app
    repository.add_goal(FinancialGoal("Keep goal", 100))
    repository.add_transaction(Transaction("income", 50, date(2024, 2, 1), "Other"))
    goals, transactions = repository.list_goals(), repository.list_transactions()
    app.run()
    next(item for item in app.text_input if item.label == "Goal name").set_value("New goal")
    next(item for item in app.text_input if item.label == "Target amount (EUR)").set_value("100")
    next(item for item in app.text_input if item.label == "Current savings (EUR)").set_value("0")
    next(item for item in app.text_input if item.label == label).set_value(str(value))
    next(item for item in app.button if item.label == submit).click().run()
    assert not app.exception
    assert any(error in item.value for item in app.error)
    assert repository.list_goals() == goals
    assert repository.list_transactions() == transactions


def test_empty_screens_offer_next_actions_and_have_no_delete_confirmation(validation_app):
    repository, app = validation_app
    app.run()
    assert not app.exception
    assert any("Create one above" in item.value for item in app.info)
    assert any("Add a transaction above" in item.value and "All categories" in item.value for item in app.info)
    assert not any(item.label == "Confirm delete" for item in app.button)
    assert repository.list_goals() == repository.list_transactions() == []


@pytest.mark.parametrize("kind", ["goal", "transaction"])
@pytest.mark.parametrize("outcome", ["confirm", "cancel", "changed", "missing"])
def test_deletion_requires_confirmation_and_protects_changed_records(validation_app, kind, outcome):
    repository, app = validation_app
    if kind == "goal":
        record_id = repository.add_goal(FinancialGoal("Selected", 100))
        other_id = repository.add_goal(FinancialGoal("Keep", 100))
        get, update, delete = repository.get_goal, repository.update_goal, repository.delete_goal
    else:
        record_id = repository.add_transaction(Transaction("income", 100, date(2024, 2, 1), "Other", "Selected"))
        other_id = repository.add_transaction(Transaction("income", 200, date(2024, 2, 1), "Other", "Keep"))
        get, update, delete = repository.get_transaction, repository.update_transaction, repository.delete_transaction
    original, other = get(record_id), get(other_id)
    app.run()
    app.date_input(key="dashboard_month").set_value(date(2024, 2, 1)).run()
    if kind == "goal":
        app.button(key=f"request_delete_goal_{record_id}").click().run()
    else:
        app.selectbox(key="transaction_to_delete").set_value(record_id).run()
        next(item for item in app.button if item.label == "Delete transaction").click().run()
    assert not app.exception
    assert get(record_id) == original
    assert any("cannot be undone" in item.value for item in app.warning)
    # An ordinary rerun is not confirmation.
    app.run()
    assert get(record_id) == original
    changed = None
    if outcome == "changed":
        changed = replace(original, saved_amount=1) if kind == "goal" else replace(original, amount=1)
        update(changed)
    elif outcome == "missing":
        delete(record_id)
    button = "cancel_deletion" if outcome == "cancel" else "confirm_deletion"
    app.button(key=button).click().run()
    assert not app.exception
    assert get(other_id) == other
    assert get(record_id) == (original if outcome == "cancel" else changed)
    assert not any(item.label == "Confirm delete" for item in app.button)
    expected_message = {"confirm": "Record deleted", "cancel": "cancelled", "changed": "Record changed", "missing": "already deleted"}[outcome]
    assert any(expected_message in item.value for item in app.info)
    app.run()
    assert not app.exception
    assert get(other_id) == other
    if kind == "transaction" and outcome == "confirm":
        assert app.metric[0].value == "200.00 EUR"


@pytest.mark.parametrize("label,submit,field", [
    ("Amount (EUR)", "Save transaction", "Transaction amount"),
    ("Target amount (EUR)", "Save goal", "Target amount"),
    ("Current savings (EUR)", "Save goal", "Current savings"),
])
@pytest.mark.parametrize("raw", [None, float("nan"), float("inf"), float("-inf"), "", "   ", "not-money", "12,34", "1,000.00", "EUR 12.50"])
def test_money_text_never_normalizes_invalid_submissions_to_defaults(validation_app, label, submit, field, raw):
    repository, app = validation_app
    repository.add_goal(FinancialGoal("Keep", 100))
    repository.add_transaction(Transaction("income", 50, date(2024, 2, 1), "Other"))
    original_goals, original_transactions = repository.list_goals(), repository.list_transactions()
    app.run()
    next(item for item in app.text_input if item.label == "Goal name").set_value("New goal")
    for money_label, value in [("Amount (EUR)", "10"), ("Target amount (EUR)", "100"), ("Current savings (EUR)", "0")]:
        next(item for item in app.text_input if item.label == money_label).set_value(value)
    # A text widget receives the browser's string spelling of NaN/inf, not a double.
    payload = None if raw is None else str(raw)
    next(item for item in app.text_input if item.label == label).set_value(payload)
    next(item for item in app.button if item.label == submit).click().run()
    assert not app.exception
    assert next(item for item in app.text_input if item.label == label).value == payload
    assert any(field in item.value for item in app.error)
    assert not app.success
    assert repository.list_goals() == original_goals
    assert repository.list_transactions() == original_transactions


@pytest.mark.parametrize("kind", ["income", "expense", "goal"])
def test_valid_decimal_text_and_zero_savings_persist_exactly_after_reopening(validation_app, kind):
    repository, app = validation_app
    amount = "9007199254740993.01"  # Beyond exact IEEE-754 integer precision.
    app.run()
    if kind == "goal":
        next(item for item in app.text_input if item.label == "Goal name").set_value("Exact target")
        next(item for item in app.text_input if item.label == "Target amount (EUR)").set_value(amount)
        next(item for item in app.text_input if item.label == "Current savings (EUR)").set_value("0")
        button = "Save goal"
    else:
        next(item for item in app.selectbox if item.label == "Type").set_value(kind)
        next(item for item in app.text_input if item.label == "Amount (EUR)").set_value(amount)
        next(item for item in app.date_input if item.label == "Date").set_value(date(2024, 2, 1))
        button = "Save transaction"
    next(item for item in app.button if item.label == button).click().run()
    assert not app.exception
    assert not app.error
    assert any("saved." in item.value for item in app.success)
    reopened = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=10).run()
    assert not reopened.exception
    if kind == "goal":
        goal = repository.list_goals()[0]
        assert goal.target_amount == Decimal(amount)
        assert goal.saved_amount == Decimal("0.00")
        assert any(f"0.00 / {amount} EUR" in item.value for item in reopened.caption)
    else:
        reopened.date_input(key="dashboard_month").set_value(date(2024, 2, 1)).run()
        assert not reopened.exception
        transaction = repository.list_transactions()[0]
        assert transaction.amount == Decimal(amount)
        assert transaction.transaction_type == kind
        assert reopened.dataframe[0].value["Amount"].tolist() == [f"{amount} EUR"]
