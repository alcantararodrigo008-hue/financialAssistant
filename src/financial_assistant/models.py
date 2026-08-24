from dataclasses import dataclass
from datetime import date
from decimal import Decimal

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


def _positive_amount(value: Decimal | float | str) -> Decimal:
    amount = Decimal(str(value))
    if amount <= 0:
        raise ValueError("The amount must be greater than zero.")
    return amount.quantize(Decimal("0.01"))


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
        if not self.name.strip():
            raise ValueError("The goal needs a name.")
        target = _positive_amount(self.target_amount)
        saved = Decimal(str(self.saved_amount)).quantize(Decimal("0.01"))
        if saved < 0:
            raise ValueError("Current savings cannot be negative.")
        if self.priority < 1:
            raise ValueError("Priority must be greater than zero.")
        if self.status not in GOAL_STATUSES:
            raise ValueError("The goal status is invalid.")
        if self.deadline is not None and not isinstance(self.deadline, date):
            raise ValueError("The deadline is invalid.")
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
        if self.transaction_type not in TRANSACTION_TYPES:
            raise ValueError("The transaction type is invalid.")
        if self.category not in CATEGORIES:
            raise ValueError("The category is invalid.")
        if not isinstance(self.transaction_date, date):
            raise TypeError("The date is invalid.")
        object.__setattr__(self, "amount", _positive_amount(self.amount))