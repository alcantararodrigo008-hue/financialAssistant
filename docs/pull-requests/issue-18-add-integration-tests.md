# PR: Complete financial-assistant integration journeys

Closes #18.

Add six isolated service journeys and one actual Streamlit submission journey.
Together they verify goal creation, income/expenses, dashboard query, persisted
calculations, goal progress and explanations. See
[Issue 18 notes](../issues/milestone-6-issue-18-add-integration-tests.md).
Production code, dependencies, schema and existing tests remain unchanged.

## Validation

- Focused integration suite: seven cases passed.
- `pytest -q`: 386 passed (41.73s).
- `python -m pytest -q`: 386 passed (49.46s).
- Ruff, dependency consistency, local links across 49 Markdown documents,
  database-ignore, whitespace and complete diff checks passed.
- Tests use temporary databases and synthetic records. Fixed service dates and
  undated UI goals avoid dependence on current goal deadlines or existing data.
- Verify exact totals/rates and chart cents, progress, recommendation evidence,
  reopening persistence, read-only database bytes and a separate untouched DB.
- AppTest checks month/year/list-filter isolation, invalid submissions, stable
  reruns, empty months and fresh sessions.
- Live Edge at 1366x900 completed actual goal/income/expense submissions, showing
  50.01 EUR net, 20% progress and matching guidance. NaN was rejected without writes;
  reload preserved records. At 390x844 the persisted dashboard/guidance rendered
  without errors or horizontal overflow. Synthetic temporary database only;
  server/browser stopped and no browser tooling added to project dependencies.

## Boundaries

Existing single-month and individual-goal heuristics remain. Transactions do not
fund goals automatically; the test verifies a separate explicit goal update.
This is regression coverage, not new UI functionality or a production security
assessment. Other browsers/physical devices, accessibility, concurrency/load,
fresh installs and minimum dependency versions are not verified.
P3 chart-sizing cleanup remains deferred.

Preserve all branches and the pre-existing instruction edits with unchanged SHA256.
Target main; GitHub's default branch differs, so manually populate the actual PR
body and do not assume automatic issue closure. Stop for independent Chat 3 review;
no merge, approval or final Senior comment by the developer.
