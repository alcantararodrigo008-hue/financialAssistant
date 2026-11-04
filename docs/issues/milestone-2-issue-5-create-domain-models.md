# Issue 5: Create domain models

Source: [Issue #5](https://github.com/alcantararodrigo008-hue/financialAssistant/issues/5).

## Acceptance criteria

- Invalid domain values are rejected with understandable errors: strengthen existing
  constructors for finite amounts, rounded positivity, calendar dates, choices, and
  field types; cover failures with parameterized tests.
- Valid goals and transactions can be created: cover all types/categories/statuses,
  optional deadlines, savings/progress, SQLite round trips, and actual app forms.
- Models remain independent of Streamlit and SQLite: standard-library-only model
  module; no new dependencies or schema changes.

See [model rules](../domain-models.md) for accepted inputs and deliberate boundaries.
Pending independent review; no approval or closure is claimed.
