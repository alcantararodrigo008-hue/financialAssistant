# PR: Create the goals screen

Closes #8 by completing the existing goals UI with active/completed separation,
visible progress, reached messages, and explainable monthly savings estimates.

## Changes and validation

- Pure Decimal estimate helper with a documented calendar-month policy and cent ceiling.
- Invalid goal submissions show model errors without writing data; save confirmation
  survives the rerun. Goal names render as plain text.
- Tests cover dated/undated creation, persistence, progress, overdue/today/completed
  and overfunded goals, leap/end-of-month cases, rounding, and Decimal context isolation.
- Both pytest entry points passed all 165 tests (138 baseline plus 27 new cases).
- Ruff, dependency checks, local Markdown links, and whitespace checks passed.
- Complete diff reviewed for financial calculations, data integrity, security,
  compatibility, and unrelated changes; no repository/model/schema changes included.
  Command results are also recorded in the actual GitHub PR description.
- Preserve uncommitted `.github/copilot-instructions.md` byte-for-byte and exclude it.

## Limitations and review

Estimates use the app's UTC date and approximate calendar months, with no interest
or affordability analysis. Goal balances/status are not automatically changed.
Existing float-based widgets have large-input precision limits. AppTest executes
the real script but does not test browser layout/live HTTP. No schema migration,
new goal edit/delete controls, or broad transaction/storage error handling.

GitHub's default branch differs from `main`; manually populate the PR description
and do not expect automatic issue closure. Pending independent Senior Engineer
review; no merge or repository settings changes are authorized.
