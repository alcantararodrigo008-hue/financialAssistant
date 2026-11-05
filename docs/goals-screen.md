# Goals screen

Open **Create goal** in the app. Enter a nonblank name, positive target amount,
current savings (enter `0` if none), optional deadline, and priority (1–5). Monetary
fields start empty and require explicit decimal text using a dot, such as `12.50`.
Blank, malformed, and non-finite values show errors rather than becoming defaults. **Save goal**
validates the model before writing through the SQLite repository. On success the
app reruns, confirms the save, and shows the new active goal. Validation errors
leave storage unchanged. The existing repository methods and schema are unchanged.

**Active goals** shows names as literal text, priority, saved/target amounts, and a
progress bar with a percentage capped at 100%. Active goals are ordered by priority,
then creation ID. A goal whose savings cover or exceed the target displays **Goal
reached!** without changing its persisted status. Previously marked completed goals
appear separately under **Completed goals**, even if their savings are below target;
this is a stored status, not evidence that the balance reached the target.

Each goal has a **Delete goal** action. It opens a record summary and requires
**Confirm delete** before removal. **Cancel deletion** preserves the record.
Changed or already-deleted records invalidate the confirmation; select again.

## Required monthly savings

The pure `required_monthly_savings(goal, as_of)` function in
`src/financial_assistant/goal_planning.py` estimates:

```text
remaining amount = target amount - current savings
monthly estimate = remaining amount / remaining calendar months
```

Count calendar months between today's date and the deadline, rounding a partial
month up to a full month. Monthly anniversaries use today's day number, clamped to
the last day of shorter months. For example, January 31 to February 28 is one
month; January 15 to April 15 is three; January 15 to April 16 is four. A future
deadline in the current month is one month. This is an approximate planning period,
not a promise that a full month remains before a near deadline.

Divide using Decimal arithmetic in a local context and round **up** to cents so
small remaining balances do not disappear. Example: 125 EUR target minus 25 EUR
saved, over three months, gives 33.34 EUR/month. Rounding may slightly overshoot
the target. The calculation neither assumes interest/returns nor assesses whether
the user's income can support that saving rate. It is educational guidance.

- No deadline: show an explicit save-at-your-own-pace message; no monthly estimate.
- Due today: explain that the remaining amount is due now; do not divide by zero.
- Overdue: show the date and suggest reviewing the deadline or remaining amount;
  no negative or misleading monthly estimate.
- Reached/overfunded: show success; no further saving is required.
- Stored completed status: no monthly saving plan, regardless of balance.

The app uses its existing UTC calendar date for goal estimates, independent of the
dashboard's selected month. Viewing goals never writes balances or changes status.
Savings recorded in a goal are manual balances; transactions do not automatically
allocate money to goals.

## Validation and limits

Unit tests cover calendar boundaries, leap years, partial months, cent rounding,
missing/past/today deadlines, completion, and caller Decimal context isolation.
Streamlit AppTest covers submissions, persistence, progress, messages, plain-text
names, and unchanged data on viewing or invalid submission. Tests use temporary
SQLite files. Browser layout and a live HTTP server are not tested. Existing
monetary text inputs, persisted money, and estimates use Decimal without a float
conversion. Amounts must fit the model's Decimal precision. Editing goals,
transaction allocation, and broad UI/storage-error handling belong to later issues.
