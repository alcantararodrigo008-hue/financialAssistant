# PR: Create validated domain models

Closes #5 by strengthening the existing immutable goal and transaction models,
adding boundary-case tests, and documenting the accepted domain values.

## Validation

- Both pytest entry points: 89 tests passed each, including temporary-database
  Streamlit form submissions and repository round trips.
- Ruff and pip dependency checks passed.
- An isolated Python process constructed both models without loading Streamlit or SQLite.
- Complete diff reviewed for validation order, constructor compatibility, edge cases,
  data/privacy concerns, and unrelated changes; local Markdown links and whitespace checked.
- Existing uncommitted instruction-file checksum remained unchanged and the file was excluded.

## Boundaries

No new dependencies, schema changes, or UI redesign. UI error presentation remains
Issue #10. Past/future dates and savings above targets are valid. Existing data is not
migrated; records violating strengthened validation will be rejected on loading.
Uncommitted `.github/copilot-instructions.md` edits remain excluded and preserved.
GitHub's default branch differs from `main`; manually populate the PR description
and do not expect automatic issue closure. No settings changes or merge are authorized.

Pending independent Senior Engineer review.

## Quantization review correction

Independently reproduced oversized finite values becoming NaN in all three money
fields with `InvalidOperation` trapping disabled; a temporary SQLite database
accepted the invalid transaction before the fix. Quantization now forces that trap
locally, converts Decimal failures to field-specific errors, and checks finiteness
after rounding. Regression tests exercise all three constructors through repository
write calls, verify no rows are written on rejection, and confirm valid amounts
still round-trip with the caller trap disabled. The actual PR description records
the final validation counts. No persistence implementation changes are included.
