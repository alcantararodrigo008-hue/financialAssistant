# Issue 12: Add dashboard visualizations

Source: [Issue #12](https://github.com/alcantararodrigo008-hue/financialAssistant/issues/12).

- Expense distribution: horizontal category bars sum only expenses from the exact
  same selected-month records used by the four dashboard metrics.
- Income/expense/net-savings trends: daily totals within the selected month, not
  cumulative values or a multi-month comparison. Only recorded dates are plotted;
  lines connect observations rather than inventing transactions on missing dates.
  Transaction-list type/category filters affect neither metrics nor charts.
- Goal progress: retain the existing capped percentage bars for active/completed
  goals, and clarify that balances are current, not historical monthly snapshots.
- Sparse data: explicit no-expense/no-transaction guidance; one-day datasets use
  visible points, a single date label, and an explanation that more dates are needed.
- Legibility: stacked full-width charts resize with the container; category labels
  are horizontal, series have colors/dashes and a bottom legend, date ticks use
  whole days, and currency axes never use fractional-cent ticks or milli-EUR labels.

Aggregation reuses the exact Decimal monthly-summary calculation. Chart values are
integer cents within JavaScript's exact integer range (`abs(cents) <= 2**53 - 1`),
with exact EUR strings in tooltips. A chart exceeding that range is replaced by
guidance to use the exact metrics/records; stored data and metric precision are not
restricted. Axis labels use compact units for large values, not financial rounding
of the underlying totals. No raw descriptions or external data sources enter charts.

Automated tests cover category/daily sums, negative savings, cents/range boundaries,
invalid values, Decimal context isolation, sparse states, selected-month filtering,
list-filter independence, valid/invalid saves, reopened persistence, and unchanged
records/goals. Live Edge checks cover desktop/mobile widths, resizing, small/empty
datasets, and goal progress. Pending independent Chat 2 Senior review.
