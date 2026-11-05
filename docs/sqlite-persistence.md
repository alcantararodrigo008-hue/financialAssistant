# SQLite persistence

`SQLiteRepository` in `src/financial_assistant/repository.py` owns all application
SQL. Streamlit calls repository methods and receives validated domain objects;
it does not execute SQL. See [domain model validation](domain-models.md).

## Storage and transactions

The default file is `data/financial_assistant.db`, resolved relative to the working
directory when the repository is constructed. Launch the app from the repository
root. The resolved path stays stable if the process later changes directories.
Missing parent directories and both tables are created automatically. Initializing
another repository for the same file preserves existing records and schema.

Each operation opens a connection, commits on success or rolls back on failure,
and closes the connection even when an exception occurs. Separate operations are
not one atomic transaction. SQLite errors (including locks or incompatible schemas)
propagate to the caller. This implementation requires a file-backed database;
`:memory:` is rejected because a new connection would have a different database.
Tests use temporary database files.

Money is stored as decimal text, never converted through SQLite floating-point
values. Dates use ISO calendar-date text. Writes revalidate models before executing
SQL, including finite amounts and positivity after rounding. Goal priority must
also fit SQLite's signed 64-bit integer range. Reads reconstruct domain objects;
invalid stored values are rejected rather than repaired. Stored recurring flags
must be 0 or 1. There is no migration or cleanup of invalid legacy records.

## Repository methods

| Method | Result |
| --- | --- |
| `add_goal(goal)` / `add_transaction(transaction)` | New integer ID; SQLite generates it regardless of the input object's optional ID; the immutable input is unchanged. |
| `get_goal(id)` / `get_transaction(id)` | Domain object with its stored ID, or `None` when missing. |
| `list_goals()` | Domain objects ordered by status, priority, then ID ascending. |
| `list_transactions(month=None, transaction_type=None, category=None)` | Matching domain objects ordered by date, then ID descending. |
| `update_goal(goal)` / `update_transaction(transaction)` | Replaces all editable fields using the object's stored ID; `True` if found, `False` if missing. Does not insert missing records. |
| `delete_goal(id)` / `delete_transaction(id)` | `True` if deleted, `False` if missing. Other records are untouched. |

IDs for get/update/delete must be actual integers from 1 through `2**63 - 1`;
booleans, missing IDs, and numeric strings are rejected with `ValueError`.
Deletion optionally accepts `expected=stored_model`. This compares the ID and all
stored fields in the DELETE statement, returning `False` if the record changed or
is missing. The UI uses this atomic snapshot check after explicit confirmation;
existing calls without `expected` retain their original ID-only behavior. A
snapshot for another ID raises `ValueError`. Values remain SQL parameters.
Create a modified frozen model with `dataclasses.replace`, preserving its ID:

```python
from dataclasses import replace
from financial_assistant.repository import SQLiteRepository

repository = SQLiteRepository()
goal = repository.get_goal(1)
if goal is not None:
    repository.update_goal(replace(goal, saved_amount="125.00"))
```

Transaction filters may be supplied separately or together (combined with AND).
Month must be an exact `YYYY-MM`, with year 0001–9999 and month 01–12. Type is
`income` or `expense`; category is one of the domain categories. `None` means no
filter; empty strings and unsupported values raise `ValueError`, rather than
silently returning all records. Existing `list_transactions("2026-11")` calls
remain supported. For example:

```python
expenses = repository.list_transactions("2026-11", "expense", "Food")
```

## Privacy and scope

All supplied SQL values use bound parameters; filter column names come from a
fixed internal list. The root `data/` contents except `.gitkeep` are ignored by
Git, including SQLite sidecars. Common `.db`, `.sqlite` and `.sqlite3` files and
their extension-based sidecars are also ignored elsewhere. Keep financial files
in `data/`; arbitrary exports or extensionless files outside it are not covered.
Git ignore rules do not encrypt data or protect it from other users of the computer. Repository operations have no external service
client. For server/telemetry settings, browser checks, OS cloud-sync risks and
other boundaries, see [privacy and security](privacy-security.md).

CRUD is provided at the repository level; the UI supports confirmed deletion and
model validation errors. Edit controls and broad storage-error presentation remain
outside this implementation. Tests cover CRUD, restart
persistence, combined filters, calendar boundaries, exact money, SQL-like input,
invalid writes, rollback, connection closure, and actual Streamlit submissions
and reopening. Browser rendering and concurrent multi-process lock behavior are
not verified by these tests.
