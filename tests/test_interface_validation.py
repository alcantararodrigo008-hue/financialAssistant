from dataclasses import replace
from datetime import date
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
    next(item for item in app.number_input if item.label == label).set_value(value)
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
