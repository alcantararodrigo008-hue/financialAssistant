from datetime import date, datetime, timezone
from decimal import Decimal, Inexact, localcontext

import pytest

from financial_assistant.goal_planning import required_monthly_savings
from financial_assistant.models import FinancialGoal


@pytest.mark.parametrize("as_of,deadline,expected", [
    (date(2026, 1, 15), date(2026, 4, 15), "33.34"),
    (date(2026, 1, 15), date(2026, 4, 16), "25.00"),
    (date(2026, 1, 15), date(2026, 1, 16), "100.00"),
    (date(2026, 1, 31), date(2026, 2, 28), "100.00"),
    (date(2024, 1, 31), date(2024, 2, 29), "100.00"),
    (date(2026, 1, 31), date(2026, 3, 1), "50.00"),
    (date(2024, 2, 29), date(2025, 2, 28), "8.34"),
    (date(2026, 12, 15), date(2027, 3, 15), "33.34"),
])
def test_estimate_uses_remaining_balance_and_calendar_months(as_of, deadline, expected):
    goal = FinancialGoal("Goal", 125, 25, deadline)
    assert required_monthly_savings(goal, as_of) == Decimal(expected)


@pytest.mark.parametrize("deadline", [None, date(2026, 1, 14), date(2026, 1, 15)])
def test_no_monthly_rate_for_missing_or_nonfuture_deadlines(deadline):
    assert required_monthly_savings(FinancialGoal("Goal", 100, deadline=deadline), date(2026, 1, 15)) is None


@pytest.mark.parametrize("saved,status", [(100, "active"), (125, "active"), (0, "completed")])
def test_reached_or_completed_goals_need_no_more_savings(saved, status):
    goal = FinancialGoal("Goal", 100, saved, status=status)
    assert required_monthly_savings(goal, date(2026, 1, 15)) == Decimal("0.00")


def test_estimate_is_independent_of_caller_decimal_precision_and_traps():
    goal = FinancialGoal("Goal", 100, deadline=date(2026, 4, 15))
    with localcontext() as context:
        context.prec = 3
        context.traps[Inexact] = True
        assert required_monthly_savings(goal, date(2026, 1, 15)) == Decimal("33.34")
        assert context.prec == 3
        assert context.traps[Inexact] is True


def test_estimate_rejects_timestamp_reference_date():
    with pytest.raises(ValueError, match="calendar date"):
        required_monthly_savings(FinancialGoal("Goal", 100), datetime(2026, 1, 15, tzinfo=timezone.utc))


def test_small_remaining_balance_rounds_up_instead_of_disappearing():
    goal = FinancialGoal("Goal", "100.00", "99.99", date(2027, 1, 1))
    assert required_monthly_savings(goal, date(2026, 1, 1)) == Decimal("0.01")
