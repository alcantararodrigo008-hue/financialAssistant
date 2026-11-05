# Issue 10: Add interface validation

Source: [Issue #10](https://github.com/alcantararodrigo008-hue/financialAssistant/issues/10).

- Invalid submissions: amount widgets allow input for validation; zero/negative
  targets and transaction amounts, negative savings, rounded-to-zero money,
  malformed dates, and blank goal names are rejected by existing models before
  writes. Errors remain visible in the form; zero savings remains valid.
- Empty screens: goals explain how to create one; transaction results suggest
  adding a record, selecting another month, or clearing type/category filters.
- Deletion: request an individual goal or selected transaction, inspect a plain-text
  summary, then explicitly confirm or cancel. Reruns do not count as confirmation.
  The confirmation retains the selected snapshot; an atomic guarded DELETE rejects
  stale or missing records. Other records remain unchanged.

Tests cover invalid amounts against existing data, empty-state next actions,
confirmation/cancellation, stale/missing records, refresh after deletion, and
repository snapshot/ID guards. Existing form/persistence/regression tests remain.
Pending independent Chat 2 Senior review; no approval or merge is claimed.
