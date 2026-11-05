# Issue 11: Add the monthly summary

Source: [Issue #11](https://github.com/alcantararodrigo008-hue/financialAssistant/issues/11).

- Selected-month income and expenses come from the repository's existing month
  filter, independent of the transaction list's type/category filters.
- Net savings is income minus expenses. The displayed savings rate is
  `net savings / income * 100`, rounded half-even to one decimal place, only when
  income is positive. Empty/expense-only months show **No income** instead of dividing.
- A selected-month heading and formula caption clarify what the four metrics mean.
- The pure `calculate_monthly_summary` helper takes already month-filtered
  transactions and returns an immutable `MonthlySummary`. It revalidates records
  and uses an isolated Decimal context with enough precision for aggregation carries.
  Totals retain cents; only the percentage is rounded. No floats or SQL aggregation.
- Saving a transaction reruns the app and rereads the month's persisted records.
  Invalid submissions leave records and displayed metrics unchanged.

Regression: two individually valid 28-digit amounts previously lost cents when
summed in the default Decimal context. Unit and AppTest checks now verify exact
large totals, as well as empty, no-income, deficit, zero-savings, cent/percentage
rounding, invalid records, caller Decimal context isolation, and restart persistence.
Existing tests cover adjacent months/years, leap dates, clearing the month,
type/category filter independence, invalid form input, and confirmed deletion refresh.

No model, repository, schema, dependency, or deletion behavior changes. Pending
independent Chat 2 Senior review; no approval or merge is claimed.
