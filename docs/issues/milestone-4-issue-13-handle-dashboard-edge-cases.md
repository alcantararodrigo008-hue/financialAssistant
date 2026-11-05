# Issue 13: Handle dashboard edge cases

Source: [Issue #13](https://github.com/alcantararodrigo008-hue/financialAssistant/issues/13).

| Scenario / criterion | Behavior and evidence |
| --- | --- |
| No income | Rate remains unavailable; explain that recorded expenses still affect the balance, without division by zero |
| No expenses | Explain that net savings equal recorded income and that unentered real-world expenses are unknown |
| Expenses exceed income | Explicit **Monthly deficit** warning with the exact shortfall; never label a deficit as a surplus |
| Deadline passed | Explicit **Overdue goal** warning, unless the balance already reached target or stored status is completed |
| No deadline | Retain save-at-your-own-pace message; no monthly estimate |
| Already complete | Preserve marked-completed/reached messages, capped progress, and no saving estimate |
| No unhandled exceptions | Combined AppTest cases exercise all goal states with empty, income-only, expense-only, deficit, balanced, tiny-balance, and large-deficit months |

Classification uses exact net savings, not the rounded rate. A one-cent deficit
remains an explicit deficit even if its rate rounds to `0.0%`. Normalize signed zero
only in the displayed percentage; do not change the actual balance. Deficit warning
amounts use context-free Decimal absolute values to retain cents in large totals.
Empty months are described as missing records rather than balanced finances.

Tests verify unchanged goals/transactions after rendering, invalid submissions, and
reopening. Month filtering remains independent of goal deadlines and list filters.
No schema, repository, model, or chart-sizing changes. The P3 Streamlit chart-sizing
deprecation remains a separate follow-up. Pending independent Chat 2 Senior review.
