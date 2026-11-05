# Guidance configuration

Recommendation percentages live in
[`guidance_config.py`](../src/financial_assistant/guidance_config.py), not in the
interface. `GuidanceConfig` is immutable and validates values when constructed.
The app explicitly passes `DEFAULT_GUIDANCE_CONFIG` to the independent rules.
Existing Python callers that omit `config` keep the same defaults.

| Setting | Default | Meaning |
| --- | --- | --- |
| `low_savings_percent` | `10` (10%) | For positive income and nonnegative net savings, flag net savings **strictly below** this percentage of income. Deficits receive a separate message. |
| `category_share_percent` | `40` (40%) | Flag an expense category **strictly above** this percentage of total recorded expenses. Income categories do not count. This is concentration, not a historical anomaly. |

Values are percentage points: `10` means 10%, not the ratio `0.10`. Finite values
from 0 through 100 are accepted, with up to 28 decimal places and no rounding.
Use `Decimal` or decimal strings for precise fractional values; integers and floats
are accepted via their string representation. Booleans, blanks, malformed values,
NaN, infinity and out-of-range values raise field-specific `ValueError`s. The decimal
place limit bounds arithmetic/display precision; it does not change money validation.

To change the application's defaults without editing `app.py`, edit the values in
`GuidanceConfig` in `guidance_config.py`, then restart the Streamlit process so Python
reloads the configuration. For example, defaults of `Decimal("20.5")` and
`Decimal("60")` would flag nonnegative savings below 20.5% and categories above 60%.
Invalid application configuration fails validation; it is not silently replaced
with defaults. There is no settings UI, external configuration file or database
storage for these settings in this issue.

Other Python callers can pass a configuration directly:

```python
from financial_assistant.guidance_config import GuidanceConfig
from financial_assistant.recommendations import recommendations

config = GuidanceConfig(low_savings_percent="20.5", category_share_percent="60")
suggestions = recommendations(transactions, goals, as_of=today, config=config)
```

At exact equality neither threshold triggers. A savings threshold of 0 disables
only the low-savings prompt; deficits are still reported. A category threshold of
100 suppresses category-share prompts; 0 flags every nonempty expense category.
Savings threshold 100 flags nonnegative savings below all recorded income, but
not an income-only month. Missing income never produces a savings-rate prompt.
Explanations show the actual configured percentages, and comparisons use exact
Decimal amounts rather than rounded dashboard rates.

Only these two existing review thresholds are configurable. Goal deadline/capacity
logic and the optional `Emergency fund` naming convention are unchanged. Guidance
uses the selected month's records independently of list filters, plus current goal
balances and today's UTC date. Reading guidance/configuration does not write goals
or transactions. Thresholds are educational prompts, not personal requirements;
single-month results are not forecasts or joint allocations among goals. No
automatic cuts to basic needs or investment recommendations are introduced.
