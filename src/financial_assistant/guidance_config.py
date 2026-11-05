"""Inspectable, validated percentages for educational guidance rules."""

from dataclasses import dataclass
from decimal import Decimal, DecimalException


@dataclass(frozen=True)
class GuidanceConfig:
    """Percentage points, not ratios: 10 means 10%, not 0.10%."""

    low_savings_percent: Decimal = Decimal(10)
    category_share_percent: Decimal = Decimal(40)

    def __post_init__(self) -> None:
        for field in ("low_savings_percent", "category_share_percent"):
            value = getattr(self, field)
            message = f"{field} must be a finite percentage from 0 to 100 with at most 28 decimal places."
            if isinstance(value, bool) or not isinstance(value, (Decimal, str, int, float)):
                raise ValueError(message)  # noqa: TRY004 - uniform configuration validation errors
            try:
                percentage = Decimal(str(value))
            except DecimalException as error:
                raise ValueError(message) from error
            if not percentage.is_finite() or not 0 <= percentage <= 100:
                raise ValueError(message)
            if percentage.as_tuple().exponent < -28:
                raise ValueError(message)
            object.__setattr__(self, field, percentage)


DEFAULT_GUIDANCE_CONFIG = GuidanceConfig()
