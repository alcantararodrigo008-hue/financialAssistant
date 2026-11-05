"""Monthly totals for validated, already month-filtered transactions."""

from collections.abc import Iterable
from dataclasses import dataclass, replace
from decimal import ROUND_HALF_EVEN, Context, Decimal, localcontext

from .models import Transaction


@dataclass(frozen=True)
class MonthlySummary:
    income: Decimal
    expenses: Decimal
    net_savings: Decimal
    savings_rate_percent: Decimal | None


def calculate_monthly_summary(transactions: Iterable[Transaction]) -> MonthlySummary:
    """Keep totals exact; round only the displayed rate to one decimal place.

    The caller supplies the selected month's records. Revalidate models so invalid
    types/amounts cannot silently corrupt totals. A fresh Decimal context prevents
    caller precision/traps from changing financial results.
    """
    records = list(transactions)
    if any(not isinstance(item, Transaction) for item in records):
        raise TypeError("Monthly summary requires Transaction records.")
    # Allow carries when adding all records, plus headroom for a percentage whose
    # denominator may be one cent. Money is never converted to binary float.
    digits = max((len(str(item.amount)) for item in records), default=1)
    precision = max(28, digits + len(str(len(records))) + 12)
    with localcontext(Context(prec=precision)):
        income = Decimal("0.00")
        expenses = Decimal("0.00")
        for item in records:
            item = replace(item)
            if item.transaction_type == "income":
                income += item.amount
            else:
                expenses += item.amount
        net = income - expenses
        rate = ((net / income) * 100).quantize(Decimal("0.1"), rounding=ROUND_HALF_EVEN) if income > 0 else None
        return MonthlySummary(income, expenses, net, rate)
