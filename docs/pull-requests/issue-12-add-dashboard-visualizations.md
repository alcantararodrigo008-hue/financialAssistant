# PR: Add dashboard visualizations

Closes #12 with expense-by-category bars and daily income/expense/net-savings lines
using the dashboard's selected-month data. Existing goal progress bars are retained
with explicit current-balance scope. No schema, model, repository, or dependency changes.

## Validation

- Unit and AppTest coverage checks exact chart/metric agreement, empty/one-day data,
  negative savings, numeric boundaries, invalid input, save/reopen persistence,
  month changes, list-only filter independence, and unchanged goal/transaction data.
- Live headless Edge rendered both charts at 1366×900, 390×844, and 360×800,
  including live resizing. Screenshots inspected; legends/date labels and cent-scale
  labels are readable, charts stay inside the viewport, and the page has no horizontal
  overflow. One-day and empty datasets and goal bars were checked; no uncaught JavaScript errors.
- Browser tooling/artifacts and seeded databases are outside the repository in
  temporary directories. Project dependencies were not changed; test servers stopped.
- Both pytest entry points passed 273 tests (255 baseline plus 18 new cases).
  Ruff, dependency checks, local links across 33 Markdown documents, ignore rules,
  and full diff/whitespace checks passed. Final results
  are recorded in the actual GitHub PR description. Preserve and exclude existing
  uncommitted instruction edits, verified by checksum.

## Boundaries

Trend scope is daily within the selected month, not historical multi-month analysis.
Charts refuse amounts beyond the exact integer-cent plotting range and direct users
to exact metrics/records. Line gaps do not establish missing-date activity. Goal
balances are current manual balances, independent of transaction month selection.
Physical-device/touch/screen-reader testing, other browsers, load/concurrency,
fresh installs, and the minimum dependency version were not tested. Existing GitHub
default-branch configuration is unchanged; populate PR descriptions manually and do
not expect automatic issue closure when targeting `main`. No approval or merge claimed.
Pending independent Senior review by Chat 2.
