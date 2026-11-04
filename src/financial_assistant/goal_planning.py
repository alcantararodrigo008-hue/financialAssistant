"""Explainable savings estimates independent of the UI and persistence."""

from calendar import monthrange
from datetime import date
from decimal import ROUND_CEILING, Context, Decimal, localcontext

from .models import FinancialGoal


def required_monthly_savings(goal: FinancialGoal, as_of: date) -> Decimal | None:
    """Return a rounded-up estimate, zero if reached/completed, or no estimate.

    Count calendar months, rounding partial months up. Monthly anniversaries
    clamp to the last day of shorter months (Jan 31 to Feb 28 is one month).
    Deadlines today or in the past require immediate attention, not a rate.
    """
    if type(as_of) is not date:
        raise ValueError("The estimate date must be a calendar date.")
    if goal.status == "completed" or goal.saved_amount >= goal.target_amount:
        return Decimal("0.00")
    if goal.deadline is None or goal.deadline <= as_of:
        return None
    months = (goal.deadline.year - as_of.year) * 12 + goal.deadline.month - as_of.month
    anniversary = date(
        goal.deadline.year, goal.deadline.month,
        min(as_of.day, monthrange(goal.deadline.year, goal.deadline.month)[1]),
    )
    months = max(1, months + (anniversary < goal.deadline))
    # Keep caller precision/traps from corrupting the estimate or changing rounding.
    precision = max(28, len(goal.target_amount.as_tuple().digits), len(goal.saved_amount.as_tuple().digits)) + 16
    with localcontext(Context(prec=precision)):
        remaining = goal.target_amount - goal.saved_amount
        return (remaining / months).quantize(Decimal("0.01"), rounding=ROUND_CEILING)
