from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from financial_assistant.models import FinancialGoal
from financial_assistant.repository import SQLiteRepository


@pytest.fixture
def goals_app(tmp_path, monkeypatch):
    app_path = Path(__file__).resolve().parents[1] / "app.py"
    monkeypatch.chdir(tmp_path)
    repository = SQLiteRepository(tmp_path / "data" / "financial_assistant.db")
    return repository, AppTest.from_file(str(app_path), default_timeout=10)


@pytest.mark.parametrize("dated", [False, True])
def test_goal_form_persists_optional_deadline_and_progress(goals_app, dated):
    repository, app = goals_app
    app.run()
    name = "[Goal](https://example.com) <script>example</script>"
    next(item for item in app.text_input if item.label == "Goal name").set_value(name)
    next(item for item in app.text_input if item.label == "Target amount (EUR)").set_value("125.00")
    next(item for item in app.text_input if item.label == "Current savings (EUR)").set_value("25.00")
    deadline = datetime.now(timezone.utc).date() + timedelta(days=1) if dated else None
    if dated:
        next(item for item in app.date_input if item.label == "Deadline (optional)").set_value(deadline)
    next(item for item in app.button if item.label == "Save goal").click().run()
    assert not app.exception
    goal = repository.list_goals()[0]
    assert (goal.name, goal.deadline, goal.priority, goal.status) == (name, deadline, 1, "active")
    assert goal.progress == 0.2
    assert any(item.value == "Goal saved." for item in app.success)
    assert any(item.value == name for item in app.text)
    assert all(name not in item.value for item in app.markdown)
    assert app.get("progress")[0].value == 20
    app.run()
    assert not app.exception
    assert len(repository.list_goals()) == 1
    if dated:
        assert any(item.value == "Required monthly savings (estimate): 100.00 EUR" for item in app.markdown)
        app.date_input(key="dashboard_month").set_value(datetime(2020, 1, 1, tzinfo=timezone.utc).date()).run()
        assert not app.exception
        assert any(item.value == "Required monthly savings (estimate): 100.00 EUR" for item in app.markdown)
    else:
        assert any("No deadline" in item.value for item in app.info)


def test_invalid_goal_submission_does_not_write(goals_app):
    repository, app = goals_app
    app.run()
    next(item for item in app.button if item.label == "Save goal").click().run()
    assert not app.exception
    assert any("name" in item.value for item in app.error)
    assert repository.list_goals() == []


@pytest.mark.parametrize("saved,status,offset,message_kind,message", [
    (0, "active", None, "info", "No deadline"),
    (0, "active", -1, "warning", "Deadline passed"),
    (0, "active", 0, "warning", "Due today"),
    (100, "active", -1, "success", "Goal reached"),
    (125, "active", 1, "success", "Goal reached"),
    (0, "completed", 1, "info", "Marked completed"),
])
def test_goal_states_are_explained_without_mutating_data(goals_app, saved, status, offset, message_kind, message):
    repository, app = goals_app
    today = datetime.now(timezone.utc).date()
    deadline = today + timedelta(days=offset) if offset is not None else None
    repository.add_goal(FinancialGoal("Existing goal", 100, saved, deadline, status=status))
    original = repository.list_goals()
    app.run()
    assert not app.exception
    assert any(message in item.value for item in getattr(app, message_kind))
    assert not any("Required monthly savings" in item.value for item in app.markdown)
    assert repository.list_goals() == original
    assert app.get("progress")[0].value == min(saved, 100)
    if status == "completed":
        assert any(item.label == "Completed goals" for item in app.expander)
        assert any("no active goals" in item.value for item in app.info)


def test_active_goals_keep_priority_order_and_completed_goals_are_separate(goals_app):
    repository, app = goals_app
    repository.add_goal(FinancialGoal("Low priority", 100, priority=5))
    repository.add_goal(FinancialGoal("Completed", 100, status="completed"))
    repository.add_goal(FinancialGoal("High priority", 100, priority=1))
    original = repository.list_goals()
    app.run()
    assert not app.exception
    # Guidance also renders plain text; check goal order independently of it.
    names = {goal.name for goal in original}
    assert [item.value for item in app.text if item.value in names] == ["High priority", "Low priority", "Completed"]
    completed = next(item for item in app.expander if item.label == "Completed goals")
    assert [item.value for item in completed.text] == ["Completed"]
    assert repository.list_goals() == original
