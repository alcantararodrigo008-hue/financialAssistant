from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from financial_assistant.models import Transaction
from financial_assistant.repository import SQLiteRepository


@pytest.fixture
def transactions_app(tmp_path, monkeypatch):
    app_path = Path(__file__).resolve().parents[1] / "app.py"
    monkeypatch.chdir(tmp_path)
    repository = SQLiteRepository(tmp_path / "data" / "financial_assistant.db")
    return repository, AppTest.from_file(str(app_path), default_timeout=10), app_path


@pytest.mark.parametrize("kind", ["income", "expense"])
@pytest.mark.parametrize("description,recurring", [("", False), ("O'Brien'); DROP TABLE transactions; -- <b>literal</b>", True)])
@pytest.mark.parametrize("amount,expected", [(0.01, "0.01"), (12.345, "12.34")])
def test_transaction_form_persists_selected_fields_and_survives_restart(transactions_app, kind, description, recurring, amount, expected):
    repository, app, app_path = transactions_app
    app.run()
    app.date_input(key="dashboard_month").set_value(date(2024, 2, 1)).run()
    next(item for item in app.selectbox if item.label == "Type").set_value(kind)
    next(item for item in app.number_input if item.label == "Amount (EUR)").set_value(amount)
    next(item for item in app.date_input if item.label == "Date").set_value(date(2024, 2, 29))
    next(item for item in app.selectbox if item.label == "Category").set_value("Food")
    next(item for item in app.text_input if item.label == "Description (optional)").set_value(description)
    next(item for item in app.checkbox if item.label == "Recurring transaction").set_value(recurring)
    next(item for item in app.button if item.label == "Save transaction").click().run()
    assert not app.exception
    assert any(item.value == "Transaction saved." for item in app.success)
    stored = repository.list_transactions()
    assert len(stored) == 1
    assert (stored[0].transaction_type, stored[0].amount, stored[0].transaction_date,
            stored[0].category, stored[0].description, stored[0].recurring) == (
        kind, Decimal(expected), date(2024, 2, 29), "Food", description, recurring,
    )
    assert app.dataframe[0].value.to_dict("records") == [{
        "Date": "2024-02-29", "Type": kind.title(), "Amount": f"{expected} EUR",
        "Category": "Food", "Description": description, "Recurring": recurring,
    }]
    # Opening a new app session reads the saved record; reruns never resubmit it.
    reopened = AppTest.from_file(str(app_path), default_timeout=10).run()
    reopened.date_input(key="dashboard_month").set_value(date(2024, 2, 1)).run()
    assert not reopened.exception
    assert reopened.dataframe[0].value.to_dict("records") == app.dataframe[0].value.to_dict("records")
    assert repository.list_transactions() == stored


@pytest.mark.parametrize("invalid_field", ["date", "amount"])
def test_invalid_transaction_does_not_write_and_can_be_corrected(transactions_app, invalid_field):
    repository, app, _ = transactions_app
    app.run()
    if invalid_field == "date":
        next(item for item in app.date_input if item.label == "Date").set_value(None)
    else:
        next(item for item in app.number_input if item.label == "Amount (EUR)").set_value(1e100)
    next(item for item in app.button if item.label == "Save transaction").click().run()
    assert not app.exception
    assert app.error
    assert not app.success
    assert repository.list_transactions() == []
    next(item for item in app.date_input if item.label == "Date").set_value(date(2024, 2, 29))
    next(item for item in app.number_input if item.label == "Amount (EUR)").set_value(1.0)
    next(item for item in app.button if item.label == "Save transaction").click().run()
    assert not app.exception
    assert len(repository.list_transactions()) == 1


@pytest.mark.parametrize("kind,category,expected_descriptions", [
    (None, None, ["food expense", "other expense", "food income", "salary"]),
    ("income", None, ["food income", "salary"]),
    ("expense", None, ["food expense", "other expense"]),
    (None, "Food", ["food expense", "food income"]),
    ("income", "Other", ["salary"]),
    ("expense", "Food", ["food expense"]),
    ("expense", "Health", []),
])
def test_transaction_filters_combine_without_changing_totals_or_data(transactions_app, kind, category, expected_descriptions):
    repository, app, _ = transactions_app
    records = [
        ("expense", "999", date(2024, 1, 31), "Food", "January"),
        ("income", "100", date(2024, 2, 1), "Other", "salary"),
        ("income", "20", date(2024, 2, 29), "Food", "food income"),
        ("expense", "10", date(2024, 2, 29), "Other", "other expense"),
        ("expense", "40", date(2024, 2, 29), "Food", "food expense"),
        ("income", "999", date(2024, 3, 1), "Other", "March"),
        ("expense", "999", date(2023, 2, 28), "Food", "Other year"),
    ]
    for record in records:
        repository.add_transaction(Transaction(*record))
    original = repository.list_transactions()
    app.run()
    app.date_input(key="dashboard_month").set_value(date(2024, 2, 1)).run()
    app.selectbox(key="transaction_type_filter").set_value(kind)
    app.selectbox(key="transaction_category_filter").set_value(category).run()
    assert not app.exception
    assert [item.value for item in app.metric][:3] == ["120.00 EUR", "50.00 EUR", "70.00 EUR"]
    if expected_descriptions:
        assert app.dataframe[0].value["Description"].tolist() == expected_descriptions
    else:
        assert not app.dataframe
        assert any("No transactions match" in item.value for item in app.info)
    app.selectbox(key="transaction_type_filter").set_value(None)
    app.selectbox(key="transaction_category_filter").set_value(None).run()
    assert len(app.dataframe[0].value) == 4
    app.date_input(key="dashboard_month").set_value(date(2024, 3, 1)).run()
    assert app.dataframe[0].value["Description"].tolist() == ["March"]
    assert repository.list_transactions() == original


def test_cleared_month_is_safe_and_can_be_selected_again(transactions_app):
    repository, app, _ = transactions_app
    repository.add_transaction(Transaction("income", 1, date(2024, 2, 29), "Other"))
    original = repository.list_transactions()
    app.run()
    app.date_input(key="dashboard_month").set_value(None).run()
    assert not app.exception
    assert any("Choose a dashboard month" in item.value for item in app.info)
    assert not app.dataframe
    assert repository.list_transactions() == original
    app.date_input(key="dashboard_month").set_value(date(2024, 2, 1)).run()
    assert not app.exception
    assert app.dataframe[0].value["Amount"].tolist() == ["1.00 EUR"]
    assert repository.list_transactions() == original
