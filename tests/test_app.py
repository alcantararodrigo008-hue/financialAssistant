import sqlite3
from datetime import date
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from financial_assistant.models import Transaction
from financial_assistant.repository import SQLiteRepository


def test_app_imports_package_and_initializes_local_database(tmp_path, monkeypatch):
    app_path = Path(__file__).resolve().parents[1] / "app.py"
    monkeypatch.chdir(tmp_path)

    app = AppTest.from_file(str(app_path), default_timeout=10).run()

    assert not app.exception
    assert app.title[0].value == "Financial Assistant"
    assert (tmp_path / "data" / "financial_assistant.db").is_file()
    assert app.metric[0].value == "0.00 EUR"


def test_valid_models_work_through_app_forms(tmp_path, monkeypatch):
    app_path = Path(__file__).resolve().parents[1] / "app.py"
    monkeypatch.chdir(tmp_path)
    app = AppTest.from_file(str(app_path), default_timeout=10).run()
    next(item for item in app.text_input if item.label == "Goal name").set_value("Emergency fund")
    next(item for item in app.number_input if item.label == "Target amount (EUR)").set_value(100.0)
    next(item for item in app.button if item.label == "Save goal").click().run()
    assert not app.exception
    next(item for item in app.number_input if item.label == "Amount (EUR)").set_value(25.0)
    next(item for item in app.button if item.label == "Guardar movimiento").click().run()
    assert not app.exception
    with sqlite3.connect(tmp_path / "data" / "financial_assistant.db") as connection:
        assert connection.execute("SELECT name FROM goals").fetchone()[0] == "Emergency fund"
        assert connection.execute("SELECT amount FROM transactions").fetchone()[0] == "25.00"

    reopened = AppTest.from_file(str(app_path), default_timeout=10).run()
    assert not reopened.exception
    assert reopened.metric[0].value == "25.00 EUR"
    assert reopened.dataframe[0].value.iloc[0]["Amount"] == "25.00 EUR"
    assert any("Emergency fund" in item.value for item in reopened.markdown)


@pytest.mark.parametrize("records,expected", [
    ([], ("0.00 EUR", "0.00 EUR", "0.00 EUR", "No income")),
    ([("income", "100.00")], ("100.00 EUR", "0.00 EUR", "100.00 EUR", "100.0%")),
    ([("expense", "40.25")], ("0.00 EUR", "40.25 EUR", "-40.25 EUR", "No income")),
    ([("income", "10"), ("expense", "12.50")], ("10.00 EUR", "12.50 EUR", "-2.50 EUR", "-25.0%")),
    ([("income", "10"), ("expense", "10")], ("10.00 EUR", "10.00 EUR", "0.00 EUR", "0.0%")),
    ([("income", "0.10"), ("income", "0.20"), ("expense", "0.10"), ("expense", "0.05")],
     ("0.30 EUR", "0.15 EUR", "0.15 EUR", "50.0%")),
])
def test_dashboard_calculates_selected_month_from_persisted_transactions(tmp_path, monkeypatch, records, expected):
    app_path = Path(__file__).resolve().parents[1] / "app.py"
    monkeypatch.chdir(tmp_path)
    repository = SQLiteRepository(tmp_path / "data" / "financial_assistant.db")
    for kind, amount in records:
        repository.add_transaction(Transaction(kind, amount, date(2024, 2, 29), "Other"))
    # Nearby months and the same month in another year must not affect totals.
    for day in (date(2024, 1, 31), date(2024, 3, 1), date(2023, 2, 28)):
        repository.add_transaction(Transaction("income", "999", day, "Other"))
        repository.add_transaction(Transaction("expense", "888", day, "Food"))
    original_records = repository.list_transactions()

    app = AppTest.from_file(str(app_path), default_timeout=10).run()
    app.date_input(key="dashboard_month").set_value(date(2024, 2, 1)).run()
    assert not app.exception
    assert {item.label: item.value for item in app.metric} == dict(zip(
        ("Income", "Expenses", "Net savings", "Savings rate"), expected, strict=True,
    ))

    app.date_input(key="dashboard_month").set_value(date(2024, 3, 1)).run()
    assert not app.exception
    assert [item.value for item in app.metric][:3] == ["999.00 EUR", "888.00 EUR", "111.00 EUR"]
    # Switching months reads persisted data without deleting or creating records.
    assert len(original_records) == len(records) + 6
    assert repository.list_transactions() == original_records
