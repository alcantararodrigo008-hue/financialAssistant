# PR: Create the transactions screen

Closes #9 by completing transaction entry and connecting existing repository
month/type/category filters to the UI. Keeps the monthly dashboard unfiltered by
type/category. No schema, model, or repository changes.

Validation: both pytest entry points passed 183 tests, including 18 new AppTest
cases with temporary SQLite data. Ruff, dependency checks, local links across 27
Markdown documents, diff/ignore checks, and exact instruction-file checksum passed.
The cleared-month regression failed before its guard was added and now passes.
Full diff reviewed for data integrity, security, and unrelated changes. Final
results are also in the actual GitHub PR description.

Limits: AppTest does not exercise a browser/live server. Existing float widgets
retain large-input precision limits; unsupported amounts are rejected by the model.
The list shows all matching records without pagination. Recurring is metadata,
not automatic transaction generation. Storage-error UI handling and edit/delete
controls remain out of scope. GitHub's default branch still differs from `main`,
so template discovery and automatic issue closure remain unavailable under this
configuration. Uncommitted instruction-file edits are preserved and excluded.

Pending independent Chat 2 Senior review. Do not merge without user authorization.
