# Issue 17: Document financial rules

## Acceptance mapping

- `docs/financial-rules.md` documents every dashboard formula: income, expenses,
  net savings, savings percentage, category totals, daily trends, goal progress and
  required monthly savings, including rounding and calendar-month counting.
- Each recommendation code has its trigger, reason, suggested review and limits.
  Defaults and strict threshold boundaries link to the existing configuration guide.
- Assumptions cover recorded-month scope, list filters, recurring metadata, manual
  current goal balances, UTC assessment date, missing data and completion precedence.
- Worked examples include normal, equality, deficit/no-income, category aggregation,
  calendar/cent-ceiling and missing-fund cases. An executable example uses actual
  pure modules without database access.
- Educational status, no investments/automatic cuts, incompleteness, forecast and
  allocation risks, technical range and storage limitations are explicit.
- README links to the guide. No application behavior or schema changes.

## Validation approach

Execute the guide's Python example against current code, run both existing pytest
entry points, Ruff/dependency checks, local Markdown links and full diff checks.
Existing regression suites already cover normal/invalid inputs, calendar edges,
persistence and data integrity. No redundant documentation snapshot tests are added.
Live application browser tests are not repeated because no UI/runtime code changes;
the existing Streamlit AppTest suite still runs. P3 chart sizing stays deferred.
