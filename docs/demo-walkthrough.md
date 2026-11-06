# Clean-data demonstration

Use the [README install steps](../README.md) in a **new clone** outside cloud-synced
folders. Start from its root, open the loopback URL and use only the synthetic
values below. Never clear, move or reset an existing user's database for this demo.
No loader or destructive reset command is provided. If an existing checkout already
has records, use another new clone/directory for an isolated demonstration.

Use one **Dashboard month** throughout. For every transaction, set **Date** to a
day in that same month; the current month is convenient. Expected figures assume
no other transactions in that month. Record each row once; if you accidentally
submit twice, totals correctly count both records. Use confirmed deletion to
remove only your unintended synthetic row.

## Walkthrough and expected results

1. **Start empty.** A new clone has no database until the app opens. Income,
   expenses and net are 0.00 EUR; rate is unavailable, goals/lists/charts show empty
   explanations, and guidance can suggest an optional emergency fund. This is not
   evidence that a person's finances are healthy.
2. **Create a goal.** Open Create goal: name `Demo trip`, target `1000`, current
   savings `250`, no deadline, priority 1. Save once. Expect 25% progress and a
   no-deadline message, with the goal's saved balance remaining 250.00 EUR.
3. **Record these synthetic transactions**, using Add transaction. Enter amounts
   as positive decimal text, select Type and Category, and choose the same month:

   | Type | Amount (EUR) | Category | Description |
   | --- | --- | --- | --- |
   | Income | 2000 | Other | Synthetic salary |
   | Expense | 500 | Housing | Synthetic rent |
   | Expense | 300 | Food | Synthetic food |
   | Expense | 200 | Transport | Synthetic transport |

   Expect income 2000.00, expenses 1000.00, net 1000.00 EUR and rate 50.0%.
   Category bars show Housing 500, Food 300, Transport 200. Housing's 50% share
   triggers a concentration review prompt, not an instruction to cut basic needs.
   The missing-emergency-fund suggestion remains optional. Goal progress is still
   25%: a transaction surplus is not an automatic goal contribution. Daily trend
   points depend on the dates you chose; a single recorded day is not a trend.
4. **Try list filters.** Select Expense and Food in the transaction list: only
   the synthetic food row appears. Dashboard totals, charts and suggestions stay
   the same. Return both filters to All before the next steps.
5. **Show low savings.** Add an Expense of `900`, category Other, description
   `Synthetic extra cost`, in the same month. Expenses become 1900.00, net 100.00
   EUR and rate 5.0%. Expect the below-10% savings explanation and Other's category
   share prompt. Goal savings/progress remain unchanged.
6. **Show a deficit.** Add another Expense of `200`, category Other, description
   `Synthetic deficit probe`, in the same month. Expenses become 2100.00, net
   -100.00 EUR and rate -5.0%. Expect an explicit deficit and its explanation,
   without a redundant low-savings prompt. No goal balance changes automatically.
7. **Reject invalid money.** Enter `NaN` in Amount and click Save transaction.
   Expect a field-specific finite-number error, no saved-success message and the
   same six transactions, totals and goal balance. Clear/correct the invalid field
   before a later valid save. Blank or malformed inputs also require correction.
8. **Confirm deletion.** Find `Synthetic deficit probe` in the transaction table.
   In Transaction to delete, select its matching date/Expense/200.00 EUR/Other entry;
   selector labels show IDs, dates, types, amounts and categories, not descriptions.
   Click Delete transaction and verify the description in the confirmation summary.
   Data remains unchanged until Confirm delete. Cancel first to demonstrate that
   records are kept, then select/delete that row and explicitly Confirm delete.
   Expect five transactions, expenses 1900.00, net 100.00 EUR and rate 5.0% again.
   If the row changed meanwhile, the app refuses the stale confirmation.
9. **Reopen.** Stop with Ctrl+C, rerun the README launch command from the same
   root and choose the same month if necessary. Expect the saved goal at 25%,
   five transactions and the 2000.00/1900.00/100.00 EUR, 5.0% dashboard. A browser
   reload also rereads data, but is not the same as restarting the server process.
10. **View an empty month.** Choose a month with no demo records. Metrics become
    zero with no savings rate and empty chart/list explanations; the current goal
    remains at 25%. Return to the demo month to recover its saved dashboard.

## Interpretation and boundaries

The goal is intentionally undated so results do not depend on a deadline passing.
For monthly saving estimates, partial-month rounding, reached/overdue goals and
configurable guidance thresholds, see [financial rules](financial-rules.md).
There is no UI control for editing saved balances or completion status; do not
claim the walkthrough demonstrates those operations. The Python repository API has
update methods, but direct database edits are not part of this demonstration.

All expected results are calculated from these synthetic records, not a financial
plan for a real user. One-month guidance is not a forecast or proof of joint goal
affordability. This app has no encryption, authentication, bank reconciliation or
secure-erasure guarantee. See [privacy boundaries](privacy-security.md). Use a
new synthetic checkout for repeat demonstrations and retain any existing work.
