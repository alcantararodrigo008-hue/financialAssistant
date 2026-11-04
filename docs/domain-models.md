# Domain models

`src/financial_assistant/models.py` defines immutable `FinancialGoal` and
`Transaction` dataclasses using only Python's standard library. They do not
import Streamlit or SQLite. Invalid input raises `ValueError` with a field-specific
message; constructors do not parse date strings.

- Target and transaction amounts must be finite, positive numbers and remain
  positive after rounding to cents. Current savings must be finite and nonnegative,
  including before rounding. Decimal, integer, float, and numeric string inputs
  are converted through their string representation; booleans are rejected.
- Amounts use explicit half-even rounding to two decimal places. Values beyond
  the active Decimal context's precision are rejected with an understandable error.
- Dates must be calendar `date` objects, not `datetime` timestamps. A goal deadline
  may be `None`. Past dates and future dates are allowed; overdue-goal guidance is
  a later issue. A caller must construct valid dates, e.g. `date(2024, 2, 29)`.
- A goal needs a nonblank text name, positive integer priority, and `active` or
  `completed` status. Higher priorities are allowed; the current UI offers 1–5.
- A transaction type is `income` or `expense`. Its category must be one of Housing,
  Food, Transport, Health, Leisure, Education, Debt, Savings, or Other. Description
  is text (empty is allowed), and recurring is a boolean.
- Savings may exceed the target; progress is capped at 1. Zero savings are allowed.
  Optional IDs are persistence metadata and are not validated by these constructors.

Examples (with `src/` on the Python import path):

```python
from datetime import date
from financial_assistant.models import FinancialGoal, Transaction

goal = FinancialGoal("Emergency fund", "1000.00", deadline=None)
expense = Transaction("expense", "12.50", date(2026, 11, 4), "Food")
```

Tests cover valid values, all allowed categories/types/statuses, rounding, malformed
and non-finite amounts, invalid dates and choices, and model immutability. Streamlit
form tests and repository round trips verify compatibility using temporary data.
Displaying friendly form validation errors remains Issue #10; this change does not
alter the UI's handling of raised exceptions or migrate existing stored records.
