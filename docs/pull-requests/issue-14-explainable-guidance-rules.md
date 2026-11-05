# PR: Explainable guidance rules

Closes #14.

Adds a pure recommendations module and a dashboard guidance section. Each suggestion
explains its data and rule: monthly deficits, below-10% savings, above-40% category
share, due/overdue or potentially unaffordable goals, and optional emergency funds.
Uses exact Decimal comparisons and existing calendar-month estimates. No automatic
cuts, investments, database changes, allocations or writes.

See [Issue 14 notes](../issues/milestone-5-issue-14-explainable-guidance-rules.md)
for thresholds, missing-data behavior, scope and acceptance mapping.

## Validation

- `.venv\Scripts\pytest.exe -q`: 302 passed (113.40s).
- `.venv\Scripts\python.exe -m pytest -q`: 302 passed (98.85s).
  19 new tests cover boundaries, invalid inputs, deterministic arithmetic, goal
  exclusions and alternatives, persistence and actual Streamlit AppTest behavior.
- An existing goal-order test now isolates goal-name text from guidance text while
  still asserting priority order and separation of completed goals.
- Live Edge at 1366x900 and 390x844 verified one, zero and several suggestions,
  literal goal names, readable mobile text without horizontal overflow, no app
  exceptions/uncaught desktop JavaScript errors, and unchanged seeded records.
  Synthetic temporary database only; server stopped and artifacts outside Git.
- Ruff, pip dependency consistency, local links across 39 Markdown documents,
  whitespace and database ignore checks passed. Complete diff reviewed for financial boundaries, security,
  read-only behavior and unrelated changes.
- User instruction edits excluded, SHA256 verified unchanged; branches retained.

## Limitations and review

Single-month data is not a forecast; category concentration lacks a historical
baseline. Goal capacity is assessed individually, not a joint allocation. Emergency
funds use an explicit goal-name convention, including completed goals; balances
outside the app and other names are not inferred. No personalized targets.
Threshold configuration remains Issue 15; broader financial documentation remains
Issue 17. Existing P3 Streamlit chart-sizing deprecation remains untouched.
Other browsers, physical devices, accessibility, concurrency/load, fresh installs
and minimum dependency versions were not tested. No external financial service.

Targets main, which is still not the GitHub default branch. The actual PR body is
populated manually; closing keywords targeting main do not automatically close the
issue under current settings. Leave open for independent Senior review by Chat 2;
no approval, final review comment or merge performed by the developer.
