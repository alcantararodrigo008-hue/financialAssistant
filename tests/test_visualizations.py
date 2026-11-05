import json
from datetime import date
from decimal import Decimal, Inexact, localcontext

import pytest

from financial_assistant.models import Transaction
from financial_assistant.visualizations import (
    ChartRangeError,
    daily_trends_spec,
    expense_distribution_spec,
)


def test_expense_distribution_uses_exact_category_totals_and_excludes_income():
    records = [Transaction(kind, amount, date(2024, 2, 29), category) for kind, amount, category in [
        ("income", "999", "Food"), ("expense", ".10", "Food"),
        ("expense", ".20", "Food"), ("expense", "2.50", "Other"),
    ]]
    spec = expense_distribution_spec(records)
    assert spec["data"]["values"] == [
        {"Category": "Food", "Cents": 30, "Exact amount": "0.30 EUR"},
        {"Category": "Other", "Cents": 250, "Exact amount": "2.50 EUR"},
    ]
    assert spec["mark"]["type"] == "bar"
    assert spec["width"] == "container"
    assert spec["autosize"]["resize"] is True
    assert spec["encoding"]["x"]["axis"]["tickMinStep"] == 1
    json.dumps(spec, allow_nan=False)


def test_daily_trends_preserve_dates_deficits_and_series_totals():
    records = [
        Transaction("expense", 3, date(2024, 2, 29), "Food"),
        Transaction("income", 1, date(2024, 2, 1), "Other"),
        Transaction("income", 2, date(2024, 2, 1), "Other"),
    ]
    spec = daily_trends_spec(records)
    values = spec["data"]["values"]
    assert [(row["Date"], row["Series"], row["Cents"]) for row in values] == [
        ("2024-02-01", "Income", 300), ("2024-02-01", "Expenses", 0), ("2024-02-01", "Net savings", 300),
        ("2024-02-29", "Income", 0), ("2024-02-29", "Expenses", 300), ("2024-02-29", "Net savings", -300),
    ]
    assert values[-1]["Exact amount"] == "-3.00 EUR"
    assert spec["encoding"]["x"]["scale"]["type"] == "utc"
    assert spec["encoding"]["x"]["axis"]["tickCount"] == {"interval": "day", "step": 7}
    assert spec["encoding"]["y"]["scale"]["zero"] is True
    assert spec["encoding"]["y"]["axis"]["tickMinStep"] == 1
    assert spec["config"]["legend"]["orient"] == "bottom"
    assert spec["encoding"]["color"]["legend"]["orient"] == "bottom"
    assert spec["encoding"]["strokeDash"]["legend"] == spec["encoding"]["color"]["legend"]
    json.dumps(spec, allow_nan=False)


def test_empty_income_only_and_single_day_states():
    assert expense_distribution_spec([]) is None
    assert daily_trends_spec([]) is None
    records = [Transaction("income", ".01", date(2024, 2, 29), "Other")]
    assert expense_distribution_spec(records) is None
    spec = daily_trends_spec(records)
    assert spec["encoding"]["x"]["type"] == "nominal"
    assert spec["mark"]["point"]["filled"] is True
    assert len(spec["data"]["values"]) == 3


@pytest.mark.parametrize("builder", [expense_distribution_spec, daily_trends_spec])
def test_chart_range_rejects_unsafe_totals_instead_of_rounding(builder):
    records = [Transaction("expense", "90071992547409.91", date(2024, 2, 29), "Other")]
    assert any(row["Cents"] == 2**53 - 1 for row in builder(records)["data"]["values"])
    records.append(Transaction("expense", ".01", date(2024, 2, 29), "Other"))
    with pytest.raises(ChartRangeError):
        builder(records)


@pytest.mark.parametrize("builder", [expense_distribution_spec, daily_trends_spec])
@pytest.mark.parametrize("invalid", [Decimal("NaN"), Decimal("Infinity"), Decimal(-1), None, "bad"])
def test_invalid_records_are_not_plotted(builder, invalid):
    record = Transaction("expense", 1, date(2024, 2, 29), "Other")
    object.__setattr__(record, "amount", invalid)
    with pytest.raises(ValueError, match="Transaction amount"):
        builder([record])


def test_chart_preparation_preserves_decimal_context_and_inputs():
    record = Transaction("expense", "12.34", date(2024, 2, 29), "Other")
    with localcontext() as context:
        context.prec = 3
        context.traps[Inexact] = True
        assert expense_distribution_spec([record])["data"]["values"][0]["Cents"] == 1234
        assert daily_trends_spec([record])["data"]["values"][-1]["Cents"] == -1234
        assert context.prec == 3
        assert context.traps[Inexact] is True
    assert record.amount == Decimal("12.34")
