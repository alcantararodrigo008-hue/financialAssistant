from datetime import date
from pathlib import Path

from streamlit.testing.v1 import AppTest

from financial_assistant.models import FinancialGoal, Transaction
from financial_assistant.repository import SQLiteRepository


def test_monthly_metrics_refresh_after_saves_and_survive_reopening(tmp_path, monkeypatch):
    path = Path(__file__).resolve().parents[1] / "app.py"
    monkeypatch.chdir(tmp_path)
    repository = SQLiteRepository(tmp_path / "data" / "financial_assistant.db")
    repository.add_transaction(Transaction("income", 999, date(2023, 12, 31), "Other"))
    repository.add_transaction(Transaction("expense", 888, date(2025, 1, 1), "Food"))
    repository.add_goal(FinancialGoal("Not transaction income", 10000, 1000))
    app = AppTest.from_file(str(path), default_timeout=10).run()
    app.date_input(key="dashboard_month").set_value(date(2024, 2, 1)).run()
    assert not app.exception
    assert any(item.value == "Monthly summary for 2024-02" for item in app.subheader)
    assert [item.value for item in app.metric] == ["0.00 EUR", "0.00 EUR", "0.00 EUR", "No income"]
    next(item for item in app.text_input if item.label == "Amount (EUR)").set_value("100")
    next(item for item in app.date_input if item.label == "Date").set_value(date(2024, 2, 29))
    next(item for item in app.button if item.label == "Save transaction").click().run()
    assert not app.exception
    assert [item.value for item in app.metric] == ["100.00 EUR", "0.00 EUR", "100.00 EUR", "100.0%"]
    next(item for item in app.selectbox if item.label == "Type").set_value("expense")
    next(item for item in app.text_input if item.label == "Amount (EUR)").set_value("25.25")
    next(item for item in app.button if item.label == "Save transaction").click().run()
    assert not app.exception
    expected = ["100.00 EUR", "25.25 EUR", "74.75 EUR", "74.8%"]
    assert [item.value for item in app.metric] == expected
    original = repository.list_transactions()
    next(item for item in app.text_input if item.label == "Amount (EUR)").set_value("0")
    next(item for item in app.button if item.label == "Save transaction").click().run()
    assert not app.exception
    assert app.error
    assert [item.value for item in app.metric] == expected
    assert repository.list_transactions() == original
    reopened = AppTest.from_file(str(path), default_timeout=10).run()
    reopened.date_input(key="dashboard_month").set_value(date(2024, 2, 1)).run()
    assert not reopened.exception
    assert [item.value for item in reopened.metric] == expected
    reopened.date_input(key="dashboard_month").set_value(date(2025, 1, 1)).run()
    assert not reopened.exception
    assert [item.value for item in reopened.metric] == ["0.00 EUR", "888.00 EUR", "-888.00 EUR", "No income"]
    assert repository.list_transactions() == original


def test_dashboard_displays_exact_large_persisted_totals(tmp_path, monkeypatch):
    path = Path(__file__).resolve().parents[1] / "app.py"
    monkeypatch.chdir(tmp_path)
    repository = SQLiteRepository(tmp_path / "data" / "financial_assistant.db")
    for _ in range(2):
        repository.add_transaction(Transaction("income", "99999999999999999999999999.99", date(2024, 2, 29), "Other"))
    repository.add_transaction(Transaction("expense", ".01", date(2024, 2, 29), "Food"))
    app = AppTest.from_file(str(path), default_timeout=10).run()
    app.date_input(key="dashboard_month").set_value(date(2024, 2, 1)).run()
    assert not app.exception
    assert [item.value for item in app.metric] == [
        "199999999999999999999999999.98 EUR", "0.01 EUR", "199999999999999999999999999.97 EUR", "100.0%",
    ]
