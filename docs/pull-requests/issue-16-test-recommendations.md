# PR: Recommendation rule regressions

Closes #16.

Add 25 focused cases covering each initial guidance rule's trigger, counterexample
and explanation. See [Issue 16 coverage](../issues/milestone-5-issue-16-test-recommendations.md).
No production behavior, dependency, database schema or chart API changes.

## Validation

- Focused rule suite: 25 passed.
- `pytest -q`: 379 passed (41.00s).
- `python -m pytest -q`: 379 passed (49.15s).
- Ruff, dependency consistency, local links across 44 Markdown documents and
  repository/whitespace checks passed. Only data/.gitkeep is tracked.
- Unit coverage checks exact financial evidence, explanation safeguards,
  category aggregation, calendar boundaries, no-data behavior and fund matching.
- SQLite regression checks deterministic results after reopening/reordering,
  invalid-record rejection under disabled Decimal traps, unchanged rows and bytes.
- Streamlit AppTest submits valid records, prevents duplicate-on-rerun regressions,
  checks pending versus confirmed deletion and reopening persistence.
- Live Edge at 1366x900 and 390x844 showed savings/category/goal-capacity/fund
  explanations as literal text, with no errors or horizontal overflow and unchanged
  synthetic records. Temporary server/browser stopped; artifacts outside the repo.
- Complete diff inspected for meaningful assertions, deterministic fixtures,
  synthetic data, financial correctness and unrelated changes.

## Scope and limitations

Tests enforce current single-month, independent-goal and name-based emergency-fund
heuristics; these do not establish personalized affordability or detect funds
outside the app. All databases/artifacts are temporary and excluded from Git.
Existing tests remain intact. P3 chart-sizing cleanup stays deferred. Physical
devices, other browsers, accessibility, concurrency/load, fresh installs and minimum
dependency versions are not verified in this issue.

Preserve user instruction edits exactly and retain every branch. Target main;
GitHub's default branch differs, so manually populate the actual PR body and do not
assume closing keywords close the issue automatically. Leave open for independent
Chat 3 review; no merge, approval or final Senior comment by the developer.
