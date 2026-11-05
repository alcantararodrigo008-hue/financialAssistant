"""Deterministic educational guidance; no persistence, UI, or investment advice."""

from collections.abc import Iterable
from dataclasses import dataclass, replace
from datetime import date
from decimal import Context, Decimal, localcontext

from .goal_planning import required_monthly_savings
from .models import FinancialGoal, Transaction
from .monthly_summary import calculate_monthly_summary


@dataclass(frozen=True)
class Recommendation:
    code: str
    explanation: str


def recommendations(
    transactions: Iterable[Transaction], goals: Iterable[FinancialGoal], *, as_of: date,
) -> tuple[Recommendation, ...]:
    """Use one selected month's transactions and current goal balances.

    Initial review thresholds: savings below 10% of income; a category above
    40% of expenses. Compare exact amounts, not rounded dashboard percentages.
    An existing goal named 'Emergency fund' (case/whitespace insensitive)
    suppresses the optional emergency-fund prompt. No historical baseline or
    automatic allocation/cuts are inferred. Each goal is assessed separately.
    """
    if type(as_of) is not date:
        raise ValueError("The guidance date must be a calendar date.")
    records = list(transactions)
    goal_records = list(goals)
    if any(not isinstance(goal, FinancialGoal) for goal in goal_records):
        raise TypeError("Guidance requires FinancialGoal records.")
    summary = calculate_monthly_summary(records)
    digits = max([len(str(summary.income)), len(str(summary.expenses)),
                  *(len(str(goal.target_amount)) + len(str(goal.saved_amount)) for goal in goal_records)])
    result = []
    with localcontext(Context(prec=max(40, digits + 20))):
        goal_records = [replace(goal) for goal in goal_records]
        if summary.net_savings < 0:
            result.append(Recommendation("deficit", f"Recorded expenses exceed income by {summary.net_savings.copy_abs():.2f} EUR this month. Review missing income, bills and timing before planning savings; protect basic needs."))
        elif summary.income > 0 and summary.net_savings * 100 < summary.income * 10:
            result.append(Recommendation("low_savings", f"Recorded net savings are {summary.net_savings:.2f} EUR against income of {summary.income:.2f} EUR: below the initial 10% review threshold. Consider a realistic savings amount after essential costs; this threshold is not a personal requirement."))
        categories = {}
        for item in records:
            if item.transaction_type == "expense":
                categories[item.category] = categories.get(item.category, Decimal(0)) + item.amount
        for category, amount in sorted(categories.items()):
            if amount * 100 > summary.expenses * 40:
                result.append(Recommendation("category_share", f"{category} accounts for {amount:.2f} EUR of {summary.expenses:.2f} EUR recorded expenses, above the initial 40% category-share threshold. Review whether the records and costs fit your situation. This is concentration, not evidence of unusual historical spending; do not automatically cut basic needs."))
        available = max(summary.net_savings, Decimal(0))
        for goal in sorted(goal_records, key=lambda goal: (goal.priority, goal.name, goal.goal_id or 0)):
            if goal.status == "completed" or goal.saved_amount >= goal.target_amount or goal.deadline is None:
                continue
            remaining = goal.target_amount - goal.saved_amount
            required = required_monthly_savings(goal, as_of)
            if goal.deadline <= as_of:
                result.append(Recommendation("goal_deadline", f"Goal {goal.name!r} has {remaining:.2f} EUR remaining and a deadline of {goal.deadline.isoformat()} (today or past). Consider a later deadline or revise the target; the original deadline leaves no future saving period."))
            elif records and required > available:
                result.append(Recommendation("goal_capacity", f"Goal {goal.name!r} needs approximately {required:.2f} EUR per month, but this month's recorded nonnegative surplus is {available:.2f} EUR. Consider saving the required amount only if affordable, extending the deadline, or revising the target. One month is not a forecast; goals compete for the same surplus and no money is automatically allocated."))
        if not any(" ".join(goal.name.casefold().split()) == "emergency fund" for goal in goal_records):
            result.append(Recommendation("emergency_fund", "No goal named 'Emergency fund' is recorded. If useful and affordable after basic needs, consider creating one for unexpected costs. An existing fund outside this app is not detected; no investment or fixed target is suggested."))
    return tuple(result)
