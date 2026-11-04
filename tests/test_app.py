from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_app_imports_package_and_initializes_local_database(tmp_path, monkeypatch):
    app_path = Path(__file__).resolve().parents[1] / "app.py"
    monkeypatch.chdir(tmp_path)

    app = AppTest.from_file(str(app_path)).run()

    assert not app.exception
    assert app.title[0].value == "Financial Assistant"
    assert (tmp_path / "data" / "financial_assistant.db").is_file()
    assert app.metric[0].value == "0.00 EUR"
