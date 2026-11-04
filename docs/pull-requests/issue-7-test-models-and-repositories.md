# PR: Test models and repositories

## Summary

Closes #7 by filling the remaining calculation coverage gap and strengthening
repository regressions, reusing existing model/CRUD coverage from Issues #5 and #6.

## Scope and validation

- Add actual Streamlit dashboard metric checks against temporary SQLite records,
  including month selection changes, financial edge cases, and exact-cent totals.
- Expand invalid model insert/update regression coverage to negative and oversized
  amounts as well as NaN, preserving existing rows and rejecting new invalid rows.
- Add year-boundary month filtering checks.
- Both pytest entry points passed all 138 tests (125-test baseline plus 13 cases).
- Ruff, dependency checks, local Markdown links, and full diff/whitespace checks passed.
- Reviewed the complete diff for bugs, data integrity, security, and unrelated changes;
  only tests and issue/PR documentation are included. Final results are also recorded
  in the actual PR description.
- Preserve and exclude existing uncommitted `.github/copilot-instructions.md` edits.

## Limitations

AppTest executes the application but does not exercise browser rendering or a live
HTTP server. No concurrency/load testing or fresh dependency installation. No
coverage percentage is claimed; the issue requirements are mapped to specific
tests in the [issue notes](../issues/milestone-2-issue-7-test-models-and-repositories.md).
The GitHub default branch still differs from `main`, so template discovery and
automatic issue closure remain subject to the documented configuration limitation.
No settings changes, merge, or approval are claimed. Pending independent review.
