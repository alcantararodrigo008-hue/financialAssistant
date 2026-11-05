# Issue 9: Create the transactions screen

Source: [Issue #9](https://github.com/alcantararodrigo008-hue/financialAssistant/issues/9).

- Record income/expenses with the shared Type selector, category/date selection,
  optional description, and recurring flag; show validation errors before writing.
- Show recent transactions newest first (date, then ID descending), including date,
  type, amount, category, description, and recurring status.
- Use Dashboard month for month selection; combine type/category filters with AND.
  All types/categories removes those restrictions. List filters do not change
  dashboard totals or persisted records; unmatched filters show an explicit empty state.
  Clearing the month requests a selection without querying or writing transactions.
- AppTest covers both types, cent rounding, optional/literal descriptions, restart
  persistence, invalid inputs/recovery, combined filters, ordering, and calendar boundaries.

Uses existing models/repository without schema or dependency changes. Pending
independent Senior review; no approval or closure is claimed.
