# Issue 8: Create the goals screen

Source: [Issue #8](https://github.com/alcantararodrigo008-hue/financialAssistant/issues/8).

## Acceptance criteria and tasks

| Requirement | Implementation and verification |
| --- | --- |
| Create a goal from the interface | Existing form now handles validation before saving; AppTest submits both dated and undated goals and verifies persistence |
| Show active goals | Active list with empty state, priority order, and separate completed expander; AppTest verifies stored completion remains separate |
| Visual progress | Bar and percentage, capped at 100%; AppTest covers partial and overfunded balances |
| Calculate monthly savings with a deadline | Pure Decimal calculation with explicit calendar-month/rounding policy; unit tests and actual UI estimate assertion |
| Report reached goals | Balance-based success message, including overdue/overfunded goals, without changing stored status |
| Goals without deadlines remain understandable | Explicit no-deadline message and no estimate; creation and rendering tested |

Dependencies already present: validated immutable models, SQLite repository, and
Streamlit. No new dependency or schema change. Risks addressed: division by zero,
negative/rounded-down estimates, Decimal caller context, accidental status changes,
invalid form writes, and user names interpreted as Markdown.

See [goals screen rules and limitations](../goals-screen.md). Pending independent
Senior Engineer review; no approval or closure is claimed.
