# Issue 18: Integration tests

## Acceptance mapping

The new `tests/test_integration.py` joins real models, file-backed SQLite,
monthly summary, chart builders, goal planning and recommendations. No production
code or schema changes are needed.

- **Isolated database:** every case uses pytest `tmp_path`; no real user data.
  Service journeys create a second database sentinel and verify its bytes stay
  unchanged, guarding against accidental cross-database access.
- **Persistence and calculations together:** create a goal, persist income and
  expense records, reopen SQLite, query a fixed month, verify exact totals/rates,
  chart values, progress, calendar saving requirement and recommendation facts.
  Repeated reads leave rows and database bytes unchanged. Explicitly funding the
  goal changes progress/guidance without altering any transactions.
- **Repeatability:** fixed calendar dates and synthetic money; same results for
  fresh/reopened repositories. Neighboring months and the same month in another
  year are excluded. Six scenarios cover surplus, low savings, deficit, no income,
  balanced and missing data.
- **Interface journey:** Streamlit AppTest submits a goal and income/expenses,
  verifies exact dashboard/progress/guidance, month/list-filter isolation, no
  duplicate-on-rerun, invalid transaction/goal submissions without partial changes,
  an empty-month round trip and a fresh app session with persisted records.
  The goal is undated so these assertions do not depend on the system clock.

Existing focused suites retain exhaustive invalid-input and confirmed/stale-deletion
coverage; this issue does not duplicate every permutation or redesign app services.
All previous tests and P3 chart-sizing APIs remain unchanged.
