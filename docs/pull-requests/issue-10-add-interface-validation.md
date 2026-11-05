# PR: Add interface validation

Closes #10 with understandable amount errors, actionable empty states, and explicit
confirmed deletion for goals and transactions. No new dependency or schema changes.

The UI always passes the confirmed snapshot to the repository's optional `expected`
delete parameter. A single parameterized DELETE compares all stored fields and ID,
so changes after the confirmation request do not cause stale data to be deleted.
Existing ID-only deletion calls remain compatible. Cancellation/reruns never delete.

Validation: both pytest entry points passed 233 tests (183 baseline plus 50 new
cases); Ruff and dependency checks passed. Local links across 29 Markdown documents,
ignore rules, and whitespace checks passed. Complete diff reviewed for input
validation, confirmation identity, data integrity, parameterized SQL, and unrelated
changes. AppTest exercises actual forms and deletion with temporary SQLite files;
final command results are also in the GitHub PR description.
Uncommitted instruction edits are preserved byte-for-byte and excluded.

Limitations: no browser/live HTTP or fresh-install testing; no general storage-error
presentation or undo/recycle bin. Money is now decimal text without float conversion;
values must fit the model's Decimal precision. Legacy noncanonical database values may
fail snapshot matching safely rather than being migrated. GitHub default-branch
configuration is unchanged, so the template is populated manually and main-targeted
closing keywords do not auto-close issues. Pending independent Chat 2 review.

## Senior review correction: preserve invalid monetary input

Independently reproduced all nine None/NaN/infinity cases silently saving defaults
through the old number widgets. All three monetary fields now start empty as text
inputs (`value=None`) and pass directly to Decimal model validation. Missing input
cannot fall back to a valid default. Tests submit missing, non-finite, empty,
whitespace, and malformed text to each field, require field-specific errors/no
success, and verify unchanged records. Valid values beyond binary float precision
and explicit zero savings are verified after reopening. Confirmation and atomic
stale-deletion guards are unchanged. Final validation totals are in the PR description.
