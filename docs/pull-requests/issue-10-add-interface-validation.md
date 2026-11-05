# PR: Add interface validation

Closes #10 with understandable amount errors, actionable empty states, and explicit
confirmed deletion for goals and transactions. No new dependency or schema changes.

The UI always passes the confirmed snapshot to the repository's optional `expected`
delete parameter. A single parameterized DELETE compares all stored fields and ID,
so changes after the confirmation request do not cause stale data to be deleted.
Existing ID-only deletion calls remain compatible. Cancellation/reruns never delete.

Validation: both pytest entry points passed 200 tests (183 baseline plus 17 new
cases); Ruff and dependency checks passed. Local links across 29 Markdown documents,
ignore rules, and whitespace checks passed. Complete diff reviewed for input
validation, confirmation identity, data integrity, parameterized SQL, and unrelated
changes. AppTest exercises actual forms and deletion with temporary SQLite files;
final command results are also in the GitHub PR description.
Uncommitted instruction edits are preserved byte-for-byte and excluded.

Limitations: no browser/live HTTP or fresh-install testing; no general storage-error
presentation or undo/recycle bin. Existing float-widget precision limits remain;
unsupported values fail model validation. Legacy noncanonical database values may
fail snapshot matching safely rather than being migrated. GitHub default-branch
configuration is unchanged, so the template is populated manually and main-targeted
closing keywords do not auto-close issues. Pending independent Chat 2 review.
