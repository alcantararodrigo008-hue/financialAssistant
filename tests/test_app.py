import sqlite3
from pathlib import Path

from streamlit.testing.v1 import AppTest


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
