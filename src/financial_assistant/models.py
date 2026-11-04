from dataclasses import dataclass
from datetime import date
from decimal import (
    ROUND_HALF_EVEN,
    Decimal,
    DecimalException,
    InvalidOperation,
    localcontext,
)

GOAL_STATUSES = {"active", "completed"}
TRANSACTION_TYPES = {"income", "expense"}
CATEGORIES = {
    "Housing",
    "Food",
    "Transport",
    "Health",
    "Leisure",
    "Education",
    "Debt",
    "Savings",
    "Other",
}


def _amount(value: Decimal | float | str, label: str, *, allow_zero: bool = False) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (Decimal, int, float, str)):
        raise ValueError(f"{label} must be a finite number.")  # noqa: TRY004 - uniform domain validation errors
    try:
        amount = Decimal(str(value))
        if not amount.is_finite():
            raise ValueError(f"{label} must be a finite number.")
        if amount < 0 or (not allow_zero and amount == 0):
            requirement = "cannot be negative" if allow_zero else "must be greater than zero"
            raise ValueError(f"{label} {requirement}.")
        with localcontext() as context:
            context.rounding = ROUND_HALF_EVEN
            # Caller trap settings must not let failed quantization return NaN.
            context.traps[InvalidOperation] = True
            rounded = amount.quantize(Decimal("0.01"))
    except DecimalException as error:
        raise ValueError(f"{label} must be a valid number within supported decimal precision.") from error
    if not rounded.is_finite():
        raise ValueError(f"{label} must be finite after rounding.")
    if not allow_zero and rounded == 0:
        raise ValueError(f"{label} must be at least 0.01 after rounding.")
    return rounded


def _calendar_date(value: date, label: str) -> None:
    # datetime subclasses date, but its timestamp does not match our date-only storage.
    if type(value) is not date:
        raise ValueError(f"{label} must be a calendar date, not a timestamp or string.")


def _choice(value: str, allowed: set[str], label: str) -> None:
    if not isinstance(value, str) or value not in allowed:
        raise ValueError(f"{label} must be one of: {', '.join(sorted(allowed))}.")


@dataclass(frozen=True)
class FinancialGoal:
    name: str
    target_amount: Decimal
    saved_amount: Decimal = Decimal(0)
    deadline: date | None = None
    priority: int = 1
    status: str = "active"
    goal_id: int | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("The goal needs a name.")
        target = _amount(self.target_amount, "Target amount")
        saved = _amount(self.saved_amount, "Current savings", allow_zero=True)
        if type(self.priority) is not int or self.priority < 1:
            raise ValueError("Priority must be a positive integer.")
        _choice(self.status, GOAL_STATUSES, "Goal status")
        if self.deadline is not None:
            _calendar_date(self.deadline, "Deadline")
        object.__setattr__(self, "target_amount", target)
        object.__setattr__(self, "saved_amount", saved)

    @property
    def progress(self) -> float:
        return min(float(self.saved_amount / self.target_amount), 1.0)


@dataclass(frozen=True)
class Transaction:
    transaction_type: str
    amount: Decimal
    transaction_date: date
    category: str
    description: str = ""
    recurring: bool = False
    transaction_id: int | None = None

    def __post_init__(self) -> None:
        _choice(self.transaction_type, TRANSACTION_TYPES, "Transaction type")
        _choice(self.category, CATEGORIES, "Category")
        _calendar_date(self.transaction_date, "Transaction date")
        if not isinstance(self.description, str):
            raise ValueError("Description must be text.")  # noqa: TRY004 - uniform domain validation errors
        if type(self.recurring) is not bool:
            raise ValueError("Recurring must be true or false.")
        object.__setattr__(self, "amount", _amount(self.amount, "Transaction amount"))
