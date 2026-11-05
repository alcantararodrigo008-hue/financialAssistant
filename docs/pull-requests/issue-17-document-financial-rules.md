# PR: Document financial calculations and guidance

Closes #17.

Add an auditable financial-rules guide and README link. Describe actual dashboard
formulas, rounding, configurable defaults/boundaries, every guidance rule's reason,
worked examples, assumptions, educational limitations and risks. See
[acceptance mapping](../issues/milestone-6-issue-17-document-financial-rules.md).
Production code, tests, database schema and chart APIs remain unchanged.

## Validation

- `pytest -q`: 379 passed (37.61s).
- `python -m pytest -q`: 379 passed (37.84s).
- Ruff and dependency consistency passed; local links across 47 Markdown documents,
  whitespace, data-ignore and full diff checks passed.
- Executed the guide's Python assertions against real modules; separately verified
  all monthly worked figures, tiny-deficit rounding and category aggregation.

Existing regression tests
cover normal/invalid inputs, boundaries, persistence and data integrity; no duplicate
tests are added for this documentation change. The example itself contains assertions
and never opens a database.

## Boundaries

Descriptions reflect existing single-month and individual-goal heuristics, not
personalized advice. No financial advice standards, historical anomaly detection,
settings UI, allocation, forecasts or security guarantees are introduced. No live
browser run for this documentation-only change; Streamlit AppTest runs in the full
suite. P3 Streamlit chart-sizing deprecation remains deferred unchanged.

Preserve all branches and exclude the existing instruction edits with identical
SHA256. Target main; the GitHub default branch differs, so manually fill the actual
PR description and do not assume closing keywords close the issue automatically.
Stop for independent Chat 3 review; no approval, final Senior comment or merge.
