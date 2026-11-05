# Financial calculations and guidance rules

Financial Assistant is an **educational prototype**, not professional financial
advice. Its suggestions are review prompts, not instructions to cut basic needs,
make investments, or guarantee that a goal is affordable. It does not recommend
investments, move money, connect to banks, or automatically allocate savings.

## What the dashboard measures

All money is interpreted as EUR; there is no exchange-rate conversion. The
selected **Dashboard month** includes recorded transaction dates in that calendar
month and year. Transaction-list type/category filters do not alter dashboard
metrics, charts or guidance. The recurring flag is metadata: it does not generate
future transactions or multiply an amount. Each recorded row counts once, so
accidental duplicate entries count twice.

Goals show their **current manually recorded balances**, independent of the
selected month. Their deadlines are assessed against today's UTC calendar date,
not the selected month's end. Viewing a historical month therefore combines old
transaction totals with current goal balances and today's deadlines; it is not a
historical goal snapshot. Transactions do not update goal balances or statuses.

## Dashboard formulas and rounding

Let `I` be total recorded income, `E` expenses and `N` net savings in the month.

| Display | Formula | Interpretation |
| --- | --- | --- |
| Income | `I = sum(amount for income records)` | Positive recorded income amounts, regardless of category. |
| Expenses | `E = sum(amount for expense records)` | Positive recorded expense amounts, regardless of category. |
| Net savings | `N = I - E` | Positive surplus, zero balance or negative deficit; not a bank balance or automatic goal contribution. |
| Savings rate | `100 * N / I` when `I > 0` | Displayed as a percentage, rounded half-even to one decimal place. With no income it is unavailable, not 0%. |
| Expenses by category | `E_category = sum(expense amounts in that category)` | Bars show category totals, not historical anomalies or income in that category. |
| Daily income/expenses/net | `I_day`, `E_day`, `I_day - E_day` | Same formulas grouped by recorded date inside the selected month; not cumulative or a multi-month trend. |
| Goal progress | `min(current savings / target amount, 1) * 100%` | Progress bar capped at 100%; stored savings can exceed target. |

Validated monetary inputs and stored amounts are decimal values rounded half-even
to cents. A target/transaction must remain at least 0.01 after rounding; current
savings can be zero but cannot be negative. Missing, malformed, non-finite or
unsupported-precision money is rejected rather than substituted with a default.
SQLite stores monetary decimal text. Totals and guidance use Decimal arithmetic.
Goal progress uses a floating-point ratio for its approximate percentage label and
bar; it does not change monetary balances.

The rate is rounded only for display: a 0.01 EUR deficit can display a 0.0% rate.
Signed zero is normalized, while deficit/surplus messages and rules use exact
amounts. For example, income 1000.00 and expenses 1000.01 produce net -0.01,
rate 0.0%, and an explicit deficit message.

Empty months have zero totals and no savings rate. Income-only months have a 100%
rate; expense-only months have a deficit and no rate. Charts plot only recorded
dates; a connecting line does not prove that intervening dates had zero spending.
One day produces points rather than evidence of a trend. No-expense/empty charts
show explanatory empty states. Chart axes use compact EUR units, with exact EUR
amounts in tooltips. Plotted values must fit the JavaScript exact integer-cent
range (`abs(cents) <= 2**53 - 1`); otherwise the affected chart is replaced with an
explanation, while exact metrics and transaction records remain available.

## Goal savings estimates

For an active, unfinished goal with a future deadline:

```text
remaining = target amount - current savings
base months = 12 * (deadline.year - today.year) + deadline.month - today.month
anniversary = today's day number in the deadline month,
              clamped to that month's last day
months = max(1, base months + (1 if anniversary < deadline else 0))
required monthly savings = remaining / months, rounded UP to cents
```

This rounds partial calendar months up; it does not measure elapsed days divided
by 30. January 31 to February 29, 2024 counts as one month; January 31 to March 1
counts as two. A future deadline later in the same month counts as one month,
even if only one day remains. Target 125.00 minus saved 25.00 over three months
requires 33.34 EUR per month. The cent ceiling can slightly overshoot the target.
No interest, investment return or inflation is assumed.

- Completed status or savings at/above target takes precedence: estimate zero,
  no further monthly plan. A stored completed status is not proof of funding.
- No deadline: no estimate, with a save-at-your-own-pace explanation.
- Deadline today or in the past: no monthly division; the app explains due-today
  or overdue status and the guidance suggests reviewing deadline/target.
- Reaching the target displays success but does not automatically store completed
  status. Priorities order display; they do not allocate money among goals.

## Configurable review thresholds

The app passes the immutable `GuidanceConfig` object to the independent rules.
See [guidance configuration](guidance-configuration.md) for validation, code
examples and how to change application defaults without editing the interface.
Restart the Streamlit process after changing source defaults.

| Setting | Default | Exact trigger |
| --- | --- | --- |
| `low_savings_percent` | 10 percentage points (10%) | With positive income and nonnegative net, `N * 100 < I * threshold`. |
| `category_share_percent` | 40 percentage points (40%) | For each expense category, `E_category * 100 > E * threshold`. |

Equality does not trigger either rule. These are initial educational heuristics,
not personalized requirements or universal financial standards. Configured values
must be finite from 0 through 100, with at most 28 decimal places; there is no
rounding or silent fallback. Percentage points differ from ratios: 10 means 10%,
not 0.10%. Low-savings threshold 0 disables that prompt but not deficits; category
threshold 100 suppresses category prompts, and 0 flags every nonempty category.
Only these two review thresholds are configurable; deadline/capacity logic and
emergency-fund name matching are separate fixed rules. No runtime settings UI or
database-backed settings exist.

## Why each recommendation appears

The rules return zero, one or several explanations based on the same recorded
month, current goals and the assessment date. They do not write records.

| Rule/code | Trigger and reason | Suggested review and boundaries |
| --- | --- | --- |
| Monthly deficit (`deficit`) | `N < 0`; expenses exceed income by `abs(N)`. | Review missing income, bills and timing before planning savings; protect basic needs. No redundant low-savings prompt is added for a deficit. |
| Low savings (`low_savings`) | `I > 0`, `N >= 0`, and exact savings below the configured percentage. | Shows net, income and threshold; consider realistic saving after essential costs. No income means no savings-rate comparison. |
| Category concentration (`category_share`) | An expense category exceeds the configured share of total recorded expenses. | Shows category amount, total expenses and threshold. Check records and circumstances; do not automatically cut basic needs. This is concentration, not evidence of historically unusual spending. Several categories can trigger. |
| Missed/immediate goal deadline (`goal_deadline`) | Active unfinished goal deadline is today or earlier. | Shows remaining amount and date; consider a later deadline or revised target because there is no future saving period under that deadline. Can appear even without transactions. |
| Potential goal capacity shortfall (`goal_capacity`) | Active unfinished future-dated goal's rounded-up monthly requirement exceeds `max(N, 0)`, and at least one transaction is recorded for the month. | Shows required saving and nonnegative surplus; save the required amount only if affordable, extend deadline or revise target. A month is not a forecast; goals compete for the same surplus and are assessed individually, not jointly allocated. |
| Optional emergency fund (`emergency_fund`) | No existing goal is named `Emergency fund` after case folding and normalization of outer/repeated whitespace. | Consider creating one if useful and affordable after basic needs. No fixed target or investment is suggested. Funds elsewhere or with other names are not detected. |

Completed or reached goals are excluded from deadline/capacity suggestions, and
undated goals receive neither. Any matching emergency-fund goal, including a
completed or underfunded one, suppresses the missing-fund prompt; that does not
establish adequacy. Missing transactions do not justify future capacity predictions,
but a missing fund or a passed deadline can still produce a suggestion. No triggered
rules does not establish financial health or complete records.

## Worked examples

These use default thresholds unless specified. Other rules can also trigger for
the same records; the examples describe the named rule, not an exhaustive list.

| Inputs | Result |
| --- | --- |
| Income 2000.00; expenses 1500.00 | Net 500.00; savings rate 25.0%; no deficit or low-savings prompt. |
| Income 1000.00; expenses 950.00 | Net 50.00; rate 5.0%; low-savings prompt explains the 10% threshold. |
| Income 1000.00; expenses 900.00 | Net 100.00; exactly 10%, so no low-savings prompt. Changing threshold to 20% triggers it. |
| Income 100.00; expenses 125.00 | Deficit 25.00; rate -25.0%; no redundant low-savings prompt. |
| No income; expenses 25.00 | Net -25.00; rate unavailable; deficit prompt remains. |
| Food expenses 12.00 + 18.00; Other expenses 50.00 | Food is 30/80 = 37.5%, below 40%; Other is 62.5%, above 40%. Income categorized as Food does not affect these shares. |
| Target 125.00; saved 25.00; assessed 2024-01-31; deadline 2024-04-30; recorded surplus 10.00 | Three months, required 33.34 per month, above 10.00; capacity prompt offers saving/deadline/target alternatives. |
| No records and no goals | Zero totals, rate unavailable; optional missing-emergency-fund prompt only. |

Run this self-contained example from the repository root using the project's
Python environment. It checks the key examples against the actual implementation
without creating a database or changing application records:

```python
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path.cwd() / "src"))
from financial_assistant.goal_planning import required_monthly_savings
from financial_assistant.guidance_config import GuidanceConfig
from financial_assistant.models import FinancialGoal, Transaction
from financial_assistant.monthly_summary import calculate_monthly_summary
from financial_assistant.recommendations import recommendations

as_of = date(2024, 1, 31)
records = [Transaction("income", "1000", as_of, "Other"),
           Transaction("expense", "900", as_of, "Food")]
summary = calculate_monthly_summary(records)
assert (summary.income, summary.expenses, summary.net_savings) == (
    Decimal("1000.00"), Decimal("900.00"), Decimal("100.00"))
assert summary.savings_rate_percent == Decimal("10.0")
fund = FinancialGoal("Emergency fund", "100")
assert "low_savings" not in {r.code for r in recommendations(records, [fund], as_of=as_of)}
custom = GuidanceConfig(low_savings_percent="20")
assert "low_savings" in {r.code for r in recommendations(records, [fund], as_of=as_of, config=custom)}
goal = FinancialGoal("Trip", "125", "25", date(2024, 4, 30))
assert required_monthly_savings(goal, as_of) == Decimal("33.34")
assert recommendations([], [fund], as_of=as_of) == ()
assert [r.code for r in recommendations([], [], as_of=as_of)] == ["emergency_fund"]
```

## Limitations and risks

- Missing income/expenses, duplicates, incorrect dates/categories or inconsistent
  manual goal balances change every conclusion. The app does not reconcile bank
  accounts or verify that records are complete. An expense categorized Savings
  still counts as an expense; it does not fund a goal automatically.
- One selected month's surplus can be seasonal or unrepresentative; essential
  costs, debt obligations and future shocks may be missing. A feasible individual
  goal estimate does not prove all goals can be funded together. Estimates ignore
  taxes not recorded, interest, inflation and future income changes.
- Category shares have no historical baseline; large housing, food or health costs
  may reflect unavoidable needs. Review prompts must not become automatic cuts.
- Decimal precision and chart limits are technical constraints, not financial
  suitability checks. A rounded percentage or capped progress bar can hide small
  differences; inspect exact monetary balances and explanation amounts.
- Local SQLite storage and local calculations do not imply encryption, backups,
  access control or production-grade privacy/security guarantees. See
  [SQLite persistence](sqlite-persistence.md) for storage boundaries.

The auditable implementation lives in [monthly totals](../src/financial_assistant/monthly_summary.py),
[goal estimates](../src/financial_assistant/goal_planning.py),
[models/progress](../src/financial_assistant/models.py),
[charts](../src/financial_assistant/visualizations.py) and
[recommendations](../src/financial_assistant/recommendations.py).
Regression coverage includes [rule contracts](../tests/test_recommendation_rules.py),
[thresholds](../tests/test_guidance_config.py),
[monthly totals](../tests/test_monthly_summary.py) and
[goal calendar estimates](../tests/test_goal_planning.py).
