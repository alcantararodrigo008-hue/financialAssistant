# PR: Handle dashboard edge cases

Closes #13 with explicit monthly financial-state explanations, exact deficit warnings,
and overdue-goal status. Reuses existing no-income/date/completion handling; no goal
balance/status is modified automatically and no financial advice rules are added.

Rounded percentage zero is unsigned, while deficit/surplus classification uses exact
net savings. Tests cover one-cent margins and a deficit larger than the default Decimal
precision, preventing both misleading signed zero and rounded warning amounts.

## Validation

- AppTest combines all requested goal states with normal/edge-case financial months,
  rejects invalid saves without changing records or displayed state, and verifies
  persistence after reopening. Unit tests protect rate/balance separation.
- Live headless Edge verified no-income, no-expense, tiny-deficit, balanced, and empty
  states alongside overdue/undated/completed/reached goals at desktop 1366×900 and
  mobile 390×844 widths. No horizontal overflow, app exceptions, or uncaught JavaScript
  errors; seeded goal records unchanged. Temporary server stopped; artifacts outside repo.
- Both pytest entry points passed 283 tests (273 baseline plus 10 new cases).
  Ruff, dependencies, local links across 35 Markdown documents, repository/ignore
  and whitespace checks passed. Complete diff reviewed for classification, goal
  precedence, exact deficit amounts, security, and unrelated changes. Final command
  results also appear in the GitHub PR description.
- Preserve/exclude uncommitted instruction edits and retain all branches.

## Boundaries

Messages describe recorded data only. Existing UTC date, percentage rounding, chart
range guards, manual goal balances, and date/status precedence remain. No schema/data
migration or broad storage-error handling. Other browsers, physical devices/touch,
screen readers, concurrency/load, fresh installs, and minimum dependency versions are
not tested. The P3 deprecated chart-sizing API is deliberately unchanged and remains
future cleanup. GitHub default-branch settings are unchanged; main-targeted closing
keywords do not automatically close issues. Pending independent Senior review by Chat 2.
