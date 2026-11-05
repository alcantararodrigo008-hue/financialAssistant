from dataclasses import FrozenInstanceError, replace
from datetime import date
from decimal import Decimal, localcontext
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from financial_assistant import guidance_config
from financial_assistant.guidance_config import DEFAULT_GUIDANCE_CONFIG, GuidanceConfig
from financial_assistant.models import FinancialGoal, Transaction
from financial_assistant.recommendations import recommendations
from financial_assistant.repository import SQLiteRepository

DAY = date(2024, 12, 31)
FUND = FinancialGoal("Emergency fund", 100)


def records(income="100", food="30", other="50"):
    return [Transaction(kind, amount, DAY, category) for kind, amount, category in
            [("income", income, "Other"), ("expense", food, "Food"), ("expense", other, "Other")]]


def test_defaults_are_immutable_and_preserve_existing_rules():
    assert DEFAULT_GUIDANCE_CONFIG == GuidanceConfig(Decimal(10), Decimal(40))
    with pytest.raises(FrozenInstanceError):
        DEFAULT_GUIDANCE_CONFIG.low_savings_percent = Decimal(20)
    assert recommendations(records(), [FUND], as_of=DAY) == recommendations(
        records(), [FUND], as_of=DAY, config=GuidanceConfig())


@pytest.mark.parametrize("field", ["low_savings_percent", "category_share_percent"])
@pytest.mark.parametrize("value", [None, True, False, "", " ", "bad", "10%", "NaN", "sNaN",
                                   "Infinity", "-Infinity", "-0.01", "100.01", "1e-29", [], object()])
def test_invalid_configuration_has_field_specific_errors(field, value):
    with pytest.raises(ValueError, match=field):
        GuidanceConfig(**{field: value})


@pytest.mark.parametrize("value", [0, 100, "12.5", Decimal("33.3333333333333333333333333333"), 0.1])
def test_valid_percentages_are_preserved_without_rounding(value):
    config = GuidanceConfig(value, value)
    assert config.low_savings_percent == config.category_share_percent == Decimal(str(value))


@pytest.mark.parametrize("threshold,expected", [("19.99", False), ("20", False), ("20.01", True),
                                               ("0", False), ("100", True)])
def test_changed_savings_threshold_and_strict_boundary(threshold, expected):
    result = recommendations(records(), [FUND], as_of=DAY,
                             config=GuidanceConfig(low_savings_percent=threshold))
    low = [r for r in result if r.code == "low_savings"]
    assert bool(low) == expected
    if expected:
        assert f"configured {threshold}%" in low[0].explanation


@pytest.mark.parametrize("threshold,expected", [("37.49", True), ("37.5", False), ("37.51", False),
                                               ("0", True), ("100", False)])
def test_changed_category_threshold_and_strict_boundary(threshold, expected):
    result = recommendations(records(), [FUND], as_of=DAY,
                             config=GuidanceConfig(category_share_percent=threshold))
    food = [r for r in result if r.code == "category_share" and r.explanation.startswith("Food ")]
    assert bool(food) == expected  # Food is exactly 30 / 80 = 37.5%.
    if expected:
        assert f"configured {threshold}%" in food[0].explanation


def test_extreme_settings_preserve_deficit_missing_income_and_goal_rules():
    config = GuidanceConfig(0, 100)
    goal = FinancialGoal("Trip", 100, deadline=date(2025, 1, 31))
    expense_only = [Transaction("expense", "0.01", DAY, "Food")]
    result = recommendations(expense_only, [FUND, goal], as_of=DAY, config=config)
    assert [r.code for r in result] == ["deficit", "goal_capacity"]
    assert "0.01 EUR" in result[0].explanation
    assert recommendations([], [FUND, goal], as_of=DAY, config=config) == ()
    assert [r.code for r in recommendations([], [], as_of=DAY, config=config)] == ["emergency_fund"]


def test_custom_precision_is_exact_and_caller_context_independent():
    # 1 cent / 1e25 EUR is exactly 1e-25 percent; the extra digit must count.
    data = records("10000000000000000000000000", "9999999999999999999999999.98", "0.01")
    equality = GuidanceConfig("1e-25", "100")
    above = GuidanceConfig("1.01e-25", "100")
    with localcontext() as context:
        context.prec = 2
        for signal in context.traps:
            context.traps[signal] = True
        assert recommendations(data, [FUND], as_of=DAY, config=equality) == ()
        result = recommendations(data, [FUND], as_of=DAY, config=above)
        assert [r.code for r in result] == ["low_savings"]
        assert "0.01 EUR" in result[0].explanation


def test_invalid_config_object_and_bypassed_fields_rejected_without_writes(tmp_path):
    repo = SQLiteRepository(tmp_path / "data.db")
    for item in records():
        repo.add_transaction(item)
    repo.add_goal(FUND)
    before = repo.list_transactions(), repo.list_goals()
    with pytest.raises(TypeError, match="GuidanceConfig"):
        recommendations(*before, as_of=DAY, config={})
    config = GuidanceConfig()
    object.__setattr__(config, "low_savings_percent", Decimal("NaN"))
    with pytest.raises(ValueError, match="low_savings_percent"):
        recommendations(*before, as_of=DAY, config=config)
    assert (SQLiteRepository(tmp_path / "data.db").list_transactions(), repo.list_goals()) == before


def test_app_uses_configuration_without_interface_edits_and_preserves_data(tmp_path, monkeypatch):
    path = str(Path(__file__).resolve().parents[1] / "app.py")
    monkeypatch.chdir(tmp_path)
    repo = SQLiteRepository()
    for item in records():
        repo.add_transaction(item)
    repo.add_transaction(replace(records()[0], transaction_date=date(2025, 1, 1), amount=9999))
    repo.add_goal(FUND)
    original = repo.list_transactions(), repo.list_goals()
    app = AppTest.from_file(path, default_timeout=15).run()
    app.date_input(key="dashboard_month").set_value(DAY).run()
    assert not any("below the configured" in item.value for item in app.text)
    monkeypatch.setattr(guidance_config, "DEFAULT_GUIDANCE_CONFIG", GuidanceConfig("20.01", "100"))

    def check(rendered):
        assert not rendered.exception
        texts = [item.value for item in rendered.text]
        assert any("configured 20.01%" in item for item in texts)
        assert not any("category-share threshold" in item for item in texts)
        assert [item.value for item in rendered.metric][:3] == ["100.00 EUR", "80.00 EUR", "20.00 EUR"]
        assert (repo.list_transactions(), repo.list_goals()) == original

    app.run()
    check(app)
    app.selectbox(key="transaction_type_filter").set_value("income").run()
    check(app)
    app.date_input(key="dashboard_month").set_value(date(2025, 1, 1)).run()
    assert not app.exception
    assert not any("below the configured" in item.value for item in app.text)
    app.date_input(key="dashboard_month").set_value(DAY).run()
    next(item for item in app.text_input if item.label == "Amount (EUR)").set_value("NaN")
    next(item for item in app.button if item.label == "Save transaction").click().run()
    assert app.error and not any("Transaction saved" in item.value for item in app.success)
    check(app)
    reopened = AppTest.from_file(path, default_timeout=15).run()
    reopened.date_input(key="dashboard_month").set_value(DAY).run()
    check(reopened)
