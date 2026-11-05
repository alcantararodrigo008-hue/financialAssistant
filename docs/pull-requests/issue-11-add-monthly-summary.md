# PR: Add the monthly summary

Closes #11 by completing the selected-month dashboard summary with a pure,
testable calculation and an explicit month/formula explanation. Keeps existing
metric labels, zero-income handling, filters, persistence, and form behavior.

Financial regression reproduced before implementation: summing two valid amounts
of `99999999999999999999999999.99` displayed `200000000000000000000000000.00`
instead of `199999999999999999999999999.98`. Precision now grows with input size
and record count; caller Decimal settings do not change totals or rate rounding.

Validation: both pytest entry points passed 255 tests (233 baseline plus 22 new
cases); Ruff and dependency checks passed. Markdown local links across 31 documents,
ignore rules, whitespace, and complete diff review passed. Additionally, 200
deterministic cases matched independent integer-cent totals and exact Fraction
percentage rounding. New unit tests verify totals/rates and invalid
models; AppTest exercises actual income/expense submissions, invalid-save stability,
month switching, reopened persistence, and exact large totals using temporary SQLite.
The actual GitHub PR description records final command results.

Limits: no browser/live HTTP, concurrency/load, or fresh-install testing. The helper
expects the caller to supply month-filtered records; the application uses the
existing repository filter. Savings rate is a rounded percentage, not a return or
investment recommendation. Existing model input precision limits remain; aggregated
totals may legitimately exceed an individual transaction's size. No schema or data
migration. GitHub default-branch configuration is unchanged; main-targeted closing
keywords do not automatically close issues. Uncommitted instruction edits remain
preserved and excluded. Pending independent Chat 2 review; do not merge.
