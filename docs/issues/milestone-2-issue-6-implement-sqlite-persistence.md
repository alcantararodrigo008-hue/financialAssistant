# Issue 6: Implement SQLite persistence

Source: [GitHub Issue #6](https://github.com/alcantararodrigo008-hue/financialAssistant/issues/6).

## Requirements and dependencies

- Initialize tables automatically, preserving existing data: retain the compatible
  schema and create missing directories/tables on construction.
- Implement goal and transaction CRUD: add/get/list/update/delete methods, with
  explicit behavior for invalid IDs and missing records.
- Filter transactions by month, type, and category, separately or together.
- Data survives restarts: verify a second process can reopen and retrieve records,
  and a new Streamlit session displays submitted data.
- Methods return domain objects: reconstruct Issue #5's validated immutable models
  and retain exact decimal amounts and calendar dates.
- SQL remains outside Streamlit: extend only the repository API; preserve existing
  application calls and tests.

Depends on the Issue #4 layout/import configuration and Issue #5 validated models,
already merged into `main`. No new packages or database migration are needed.
Risks addressed include SQL injection, accidental broad filters/deletes, invalid
money writes, integer overflow, transaction rollback, and leaked connections.

See [repository contracts and limitations](../sqlite-persistence.md). Tests use
synthetic temporary data. Pending independent Senior review; no approval or issue
closure is claimed.
