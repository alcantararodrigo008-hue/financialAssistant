# Issue 14: Explainable guidance rules

## Requirements and implementation

Independent, deterministic recommendations cover deficits, low savings, category
concentration, difficult goal deadlines and optional emergency funds. The UI
shows zero, one or multiple explanations as plain text, safely displaying user
names without interpreting Markdown or HTML. No database changes or writes occur.

- Deficit: exact expenses exceed income; suggest reviewing records and timing.
- Low savings: nonnegative net savings below 10% of positive income. Exact
  comparison avoids rounded-percentage boundary errors. Deficits get their own
  message instead of a redundant low-savings prompt.
- Category concentration: expense category exceeds 40% of total expenses. This
  is a share-based review prompt, not an assertion of historically unusual costs.
  Income categories do not count. Exactly 40% does not trigger.
- Active, unfinished goals: due/past deadlines prompt a later deadline or revised
  target. Future deadlines compare the existing rounded-up calendar-month saving
  estimate with max(selected-month net savings, 0), only when records exist.
  Explain saving requirements, extending deadlines or revising targets. Completed,
  reached and undated goals are excluded. Assess each goal separately; a month's
  surplus is not a forecast or an allocation shared successfully among all goals.
- Emergency fund: suggest considering an optional goal when no existing goal has
  the name `Emergency fund`, ignoring case and repeated/outer whitespace. Existing
  completed goals also count as existing; this does not assess their adequacy.
  Funds outside the app and alternative names are not detected. No fixed target.

The interface uses selected-month records, independent of transaction list filters,
and current goal balances/deadlines assessed as of today's UTC date. Missing records
do not establish financial health or justify predictions. Suggestions protect basic
needs and do not recommend automatic cuts or investments. Thresholds are initial
educational heuristics, not personalized requirements; configuration is Issue 15.

## Validation

Unit tests cover exact thresholds, no data/income, expenses only, goal alternatives,
completion exclusions, name matching, invalid models/dates, deterministic arithmetic
under hostile Decimal settings and large values. Streamlit AppTest verifies zero,
one and several messages, month/filter isolation, persisted data after reopening,
and no writes while generating guidance. Existing UI regression tests also run.

P3 Streamlit chart-sizing deprecation remains a separate follow-up, unchanged.
