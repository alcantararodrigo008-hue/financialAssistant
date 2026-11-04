# PR: Implement SQLite persistence

## Summary

Closes #6 by completing goal and transaction CRUD, adding validated transaction
filters, and keeping SQL and connection management within `SQLiteRepository`.
Existing app calls and the database schema remain compatible.

## Scope and validation

- Add single-record reads, updates, and deletes with predictable missing-ID behavior.
- Validate IDs/filters, revalidate financial models before writes, preserve decimal
  text, and close connections after commit/rollback.
- Test full CRUD, combined filters, dates and money boundaries, new-process restart
  persistence, invalid writes, SQL-like input, rollback, and connection closure.
- Exercise real Streamlit form submissions and reopening against temporary data.
- Document API contracts, privacy, acceptance criteria, and limits.

Final command results are recorded in the actual GitHub PR description. Existing
uncommitted `.github/copilot-instructions.md` work is preserved and excluded.

## Limitations and review

No new edit/delete UI or error presentation; no database encryption, migration, or
cleanup of invalid legacy records. Only file-backed databases are supported;
`:memory:` now fails clearly instead of losing tables between operations. Browser
rendering, an HTTP server, and concurrent multi-process locking were not tested.
The default branch differs from `main`; this PR explicitly targets `main`, its
description is populated manually, and automatic issue closure does not apply.
No settings changed. Pending independent Senior review; do not merge without
explicit user authorization.
