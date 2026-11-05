import json
from datetime import date
from pathlib import Path

import pyarrow as pa
from streamlit.testing.v1 import AppTest

from financial_assistant.models import FinancialGoal, Transaction
from financial_assistant.repository import SQLiteRepository


def chart_rows(app):
    result = {}
    for element in app.get("vega_lite_chart") or app.get("arrow_vega_lite_chart"):
        spec = json.loads(element.proto.spec)
        result[spec["mark"]["type"]] = pa.ipc.open_stream(element.proto.data.data).read_all().to_pylist()
        assert element.proto.use_container_width
        assert spec["autosize"]["resize"] is True
    return result


def test_charts_match_month_metrics_filters_saves_and_reopened_data(tmp_path, monkeypatch):
    path = Path(__file__).resolve().parents[1] / "app.py"
    monkeypatch.chdir(tmp_path)
    repository = SQLiteRepository(tmp_path / "data" / "financial_assistant.db")
    for kind, amount, day, category in [
        ("expense", 999, date(2024, 1, 31), "Food"),
        ("income", 100, date(2024, 2, 1), "Other"),
        ("expense", 10, date(2024, 2, 1), "Food"),
        ("expense", 20, date(2024, 2, 29), "Food"),
        ("expense", 5, date(2024, 2, 29), "Other"),
        ("income", 999, date(2024, 3, 1), "Other"),
    ]:
        repository.add_transaction(Transaction(kind, amount, day, category))
    repository.add_goal(FinancialGoal("Overfunded goal", 100, 125))
    goals = repository.list_goals()
    app = AppTest.from_file(str(path), default_timeout=10).run()
    app.date_input(key="dashboard_month").set_value(date(2024, 2, 1)).run()
    assert not app.exception
    rows = chart_rows(app)
    assert rows["bar"] == [
        {"Category": "Food", "Cents": 3000, "Exact amount": "30.00 EUR"},
        {"Category": "Other", "Cents": 500, "Exact amount": "5.00 EUR"},
    ]
    assert [item.value for item in app.metric][:3] == ["100.00 EUR", "35.00 EUR", "65.00 EUR"]
    assert sum(row["Cents"] for row in rows["line"] if row["Series"] == "Net savings") == 6500
    assert {row["Date"] for row in rows["line"]} == {"2024-02-01", "2024-02-29"}
    assert app.get("progress")[0].value == 100
    original = repository.list_transactions()
    app.selectbox(key="transaction_type_filter").set_value("income")
    app.selectbox(key="transaction_category_filter").set_value("Health").run()
    assert chart_rows(app) == rows  # List-only filters must not alter dashboard charts.
    assert not app.dataframe
    assert repository.list_transactions() == original
    next(item for item in app.selectbox if item.label == "Type").set_value("expense")
    next(item for item in app.selectbox if item.label == "Category").set_value("Other")
    next(item for item in app.date_input if item.label == "Date").set_value(date(2024, 2, 29))
    next(item for item in app.text_input if item.label == "Amount (EUR)").set_value("3.25")
    next(item for item in app.button if item.label == "Save transaction").click().run()
    assert not app.exception
    updated = chart_rows(app)
    assert updated["bar"][-1]["Cents"] == 825
    assert [item.value for item in app.metric][:3] == ["100.00 EUR", "38.25 EUR", "61.75 EUR"]
    persisted = repository.list_transactions()
    next(item for item in app.text_input if item.label == "Amount (EUR)").set_value("nan")
    next(item for item in app.button if item.label == "Save transaction").click().run()
    assert not app.exception
    assert app.error
    assert chart_rows(app) == updated
    assert repository.list_transactions() == persisted
    reopened = AppTest.from_file(str(path), default_timeout=10).run()
    reopened.date_input(key="dashboard_month").set_value(date(2024, 2, 1)).run()
    assert not reopened.exception
    assert chart_rows(reopened) == updated
    reopened.date_input(key="dashboard_month").set_value(date(2024, 3, 1)).run()
    assert not reopened.exception
    assert set(chart_rows(reopened)) == {"line"}
    assert any("Only one recorded day" in item.value for item in reopened.info)
    reopened.date_input(key="dashboard_month").set_value(date(2024, 4, 1)).run()
    assert not reopened.exception
    assert chart_rows(reopened) == {}
    assert any("No expenses this month" in item.value for item in reopened.info)
    assert any("No transactions this month" in item.value for item in reopened.info)
    assert repository.list_transactions() == persisted
    assert repository.list_goals() == goals


def test_oversized_chart_data_keeps_exact_metrics_and_explains_limit(tmp_path, monkeypatch):
    path = Path(__file__).resolve().parents[1] / "app.py"
    monkeypatch.chdir(tmp_path)
    repository = SQLiteRepository(tmp_path / "data" / "financial_assistant.db")
    repository.add_transaction(Transaction("expense", "90071992547409.92", date(2024, 2, 29), "Food"))
    app = AppTest.from_file(str(path), default_timeout=10).run()
    app.date_input(key="dashboard_month").set_value(date(2024, 2, 1)).run()
    assert not app.exception
    assert not chart_rows(app)
    assert len([item for item in app.info if "exact numeric range" in item.value]) == 2
    assert [item.value for item in app.metric][:3] == ["0.00 EUR", "90071992547409.92 EUR", "-90071992547409.92 EUR"]
