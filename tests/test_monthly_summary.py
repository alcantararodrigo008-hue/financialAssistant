from dataclasses import FrozenInstanceError
from datetime import date
from decimal import Decimal, Inexact, localcontext

import pytest

from financial_assistant.models import Transaction
from financial_assistant.monthly_summary import calculate_monthly_summary


@pytest.mark.parametrize("records,expected", [
    ([], ("0.00", "0.00", "0.00", None)),
    ([("income", "100")], ("100.00", "0.00", "100.00", "100.0")),
    ([("expense", "25.25")], ("0.00", "25.25", "-25.25", None)),
    ([("income", "100"), ("expense", "25.25")], ("100.00", "25.25", "74.75", "74.8")),
    ([("income", "10"), ("expense", "12.50")], ("10.00", "12.50", "-2.50", "-25.0")),
    ([("income", "10"), ("expense", "10")], ("10.00", "10.00", "0.00", "0.0")),
    ([("income", "0.10"), ("income", "0.20"), ("expense", "0.15")], ("0.30", "0.15", "0.15", "50.0")),
    ([("income", "2000"), ("expense", "1999")], ("2000.00", "1999.00", "1.00", "0.0")),
    ([("income", "2000"), ("expense", "1997")], ("2000.00", "1997.00", "3.00", "0.2")),
    ([("income", ".01"), ("expense", "100")], ("0.01", "100.00", "-99.99", "-999900.0")),
])
def test_monthly_totals_and_rate(records, expected):
    items = [Transaction(kind, amount, date(2024, 2, 29), "Other") for kind, amount in records]
    summary = calculate_monthly_summary(iter(items))
    values = (summary.income, summary.expenses, summary.net_savings, summary.savings_rate_percent)
    assert values == tuple(Decimal(value) if value is not None else None for value in expected)
    assert isinstance(summary.income, Decimal)
    assert isinstance(summary.expenses, Decimal)
    assert isinstance(summary.net_savings, Decimal)


def test_totals_keep_cents_when_the_sum_exceeds_default_decimal_precision():
    items = [Transaction("income", "99999999999999999999999999.99", date(2024, 2, 29), "Other") for _ in range(2)]
    items.append(Transaction("expense", "0.01", date(2024, 2, 29), "Food"))
    with localcontext() as context:
        context.prec = 3
        context.traps[Inexact] = True
        summary = calculate_monthly_summary(items)
        assert summary.income == Decimal("199999999999999999999999999.98")
        assert summary.net_savings == Decimal("199999999999999999999999999.97")
        assert summary.savings_rate_percent == Decimal("100.0")
        assert context.prec == 3
        assert context.traps[Inexact] is True
    assert items[0].amount == Decimal("99999999999999999999999999.99")
    with pytest.raises(FrozenInstanceError):
        summary.income = Decimal(0)


@pytest.mark.parametrize("value", [Decimal("NaN"), Decimal("Infinity"), Decimal(-1), Decimal(0), None, "bad"])
def test_invalid_models_cannot_corrupt_the_summary(value):
    item = Transaction("income", 1, date(2024, 2, 29), "Other")
    object.__setattr__(item, "amount", value)
    with pytest.raises(ValueError, match="Transaction amount"):
        calculate_monthly_summary([item])


@pytest.mark.parametrize("item", [None, {"amount": 1}, 1])
def test_non_transaction_inputs_are_rejected(item):
    with pytest.raises(TypeError, match="Transaction"):
        calculate_monthly_summary([item])


@pytest.mark.parametrize("expense,net", [("1000.01", "-0.01"), ("999.99", "0.01")])
def test_rounded_zero_rate_does_not_change_exact_surplus_or_deficit(expense, net):
    records = [Transaction("income", 1000, date(2024, 2, 29), "Other"),
               Transaction("expense", expense, date(2024, 2, 29), "Other")]
    summary = calculate_monthly_summary(records)
    assert summary.net_savings == Decimal(net)
    assert summary.savings_rate_percent == Decimal("0.0")
    assert not summary.savings_rate_percent.is_signed()
