# Issue 7: Test models and repositories

Source: [Issue #7](https://github.com/alcantararodrigo008-hue/financialAssistant/issues/7).

## Requirements and coverage

| Requirement | Evidence |
| --- | --- |
| Create and retrieve goals | Existing full-field CRUD, restart, and repository round-trip tests |
| Create and retrieve transactions | Existing exact-money, metadata, CRUD, and restart tests |
| Reject invalid amounts | Existing domain boundary/Decimal-trap tests; expanded repository insert/update revalidation regressions |
| Month filtering | Existing leap-day/combined filter tests; new December/January and same-month/different-year regression |
| Income, expense, savings calculations | New AppTest cases assert actual metrics from persisted rows, with literal expected totals |
| Run with pytest | Both supported pytest entry points are validated |
| Isolated temporary database | Repository fixtures and app tests use pytest temporary directories; no user database is accessed |

Dashboard cases cover empty months, income only, expenses only, deficit, equal totals,
and exact-cent sums. Adjacent months and another year's records are deliberately
seeded to detect filtering mistakes, and changing the selected month verifies
recalculation without modifying stored records.

The implementation adds tests and documentation only. No new dependencies or
production behavior changes. Pending independent Senior Engineer review.
