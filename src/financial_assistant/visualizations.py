"""Inline Vega-Lite charts built from the dashboard's month-filtered records."""

from collections import defaultdict
from collections.abc import Iterable
from datetime import date
from decimal import Decimal

from .models import Transaction
from .monthly_summary import calculate_monthly_summary


class ChartRangeError(ValueError):
    """A chart value exceeds JavaScript's exact integer-cent range."""


def _cents(amount: Decimal) -> int:
    numerator, denominator = amount.as_integer_ratio()
    cents = numerator * 100 // denominator
    if abs(cents) > 2**53 - 1:
        raise ChartRangeError("Amounts exceed the chart's exact integer-cent range.")
    return cents


def _spec(values: list[dict], height: int) -> dict:
    return {
        "data": {"values": values}, "width": "container", "height": height,
        "autosize": {"type": "fit", "contains": "padding", "resize": True},
        "config": {"legend": {"orient": "bottom", "title": None}, "view": {"stroke": None}},
    }


def _amount_axis(ticks: int) -> dict:
    return {"tickCount": ticks, "tickMinStep": 1,
            "labelExpr": "abs(datum.value) < 100000 ? format(datum.value / 100, ',.2f') : format(datum.value / 100, '.3~s')"}


def expense_distribution_spec(transactions: Iterable[Transaction]) -> dict | None:
    records = list(transactions)
    calculate_monthly_summary(records)  # Validate every record, including income.
    groups: dict[str, list[Transaction]] = defaultdict(list)
    for item in records:
        if item.transaction_type == "expense":
            groups[item.category].append(item)
    if not groups:
        return None
    values = []
    for category, items in sorted(groups.items()):
        amount = calculate_monthly_summary(items).expenses
        values.append({"Category": category, "Cents": _cents(amount), "Exact amount": f"{amount:.2f} EUR"})
    spec = _spec(values, max(120, len(values) * 30 + 50))
    spec.update({
        "mark": {"type": "bar", "color": "#D55E00"},
        "encoding": {
            "y": {"field": "Category", "type": "nominal", "sort": "-x", "title": None},
            "x": {"field": "Cents", "type": "quantitative", "title": "Expenses (EUR)",
                  "axis": _amount_axis(4)},
            "tooltip": [{"field": "Category", "type": "nominal"}, {"field": "Exact amount", "type": "nominal"}],
        },
    })
    return spec


def daily_trends_spec(transactions: Iterable[Transaction]) -> dict | None:
    records = list(transactions)
    calculate_monthly_summary(records)
    groups: dict[date, list[Transaction]] = defaultdict(list)
    for item in records:
        groups[item.transaction_date].append(item)
    if not groups:
        return None
    values = []
    for day, items in sorted(groups.items()):
        summary = calculate_monthly_summary(items)
        for label, amount in (("Income", summary.income), ("Expenses", summary.expenses), ("Net savings", summary.net_savings)):
            values.append({"Date": day.isoformat(), "Series": label, "Cents": _cents(amount), "Exact amount": f"{amount:.2f} EUR"})
    day_step = max(1, (max(groups) - min(groups)).days // 4)
    x = {"field": "Date", "type": "temporal", "title": "Date (UTC)", "scale": {"type": "utc"},
         "axis": {"format": "%d %b", "tickCount": {"interval": "day", "step": day_step}, "labelOverlap": "greedy"}}
    if len(groups) == 1:
        x = {"field": "Date", "type": "nominal", "title": "Date", "axis": {"labelAngle": 0}}
    spec = _spec(values, 250)
    spec.update({
        "mark": {"type": "line", "point": {"filled": True, "size": 55}},
        "encoding": {
            "x": x,
            "y": {"field": "Cents", "type": "quantitative", "title": "Daily amount (EUR)",
                  "scale": {"zero": True}, "axis": _amount_axis(5)},
            "color": {"field": "Series", "type": "nominal", "scale": {
                "domain": ["Income", "Expenses", "Net savings"], "range": ["#1764AB", "#D55E00", "#007A5E"],
            }, "legend": {"title": None, "orient": "bottom", "direction": "horizontal"}},
            "strokeDash": {"field": "Series", "type": "nominal", "legend": {
                "title": None, "orient": "bottom", "direction": "horizontal",
            }},
            "tooltip": [{"field": field, "type": "nominal"} for field in ("Date", "Series", "Exact amount")],
        },
    })
    return spec
