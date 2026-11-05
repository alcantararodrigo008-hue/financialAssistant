# Issue 16: Test recommendations

## Acceptance coverage

Add focused rule-contract tests to complement the existing threshold/configuration
suite. Production code, schema, dependencies and chart APIs remain unchanged.

| Requirement | Added regression evidence |
| --- | --- |
| Monthly deficit | Deficit, one-cent deficit, no income, balanced and surplus cases; exact shortfall and basic-needs explanation; no redundant low-savings prompt. |
| Low savings | Exact income/net evidence, configured threshold, essential-cost/personal-requirement limitations; equality and income-only counterexamples. |
| High category spending | Aggregate split expenses, exclude income in the same category, verify amounts/denominator/configured percentage, multiple categories, historical-baseline and basic-needs limitations. |
| Potentially unreachable goals | Remaining rather than total target, leap-day/partial-month/cent-ceiling estimates, affordable equality, due/past alternatives, completed/reached/overfunded/undated exclusions, non-forecast/non-allocation explanation. |
| Missing data | No invented income, expense or future-capacity warning; empty goals produce only the optional emergency-fund prompt. |
| Missing emergency fund | Matching names with case/whitespace normalization, completed fund, nonmatching/plural/suffixed names; optional/affordable/outside-app/non-investment explanation. |
| Data integrity and invalid input | Reordered inputs and reopened SQLite yield identical suggestions; invalid NaN record under disabled traps rejected; records and database bytes unchanged. |
| Actual interface behavior | AppTest submits a goal with zero savings and an expense, verifies guidance, no duplicate on rerun, pending deletion retains data/guidance, explicit confirmation clears both, and reopening preserves results. |

Assertions check financial facts and meaningful explanation clauses rather than
snapshotting every sentence. Existing tests retain custom thresholds, malformed
inputs, context/precision, month/filter isolation and invalid-form coverage.

## Boundaries

Use synthetic data and temporary databases only. Tests enforce existing documented
heuristics, not personalized financial advice or historical anomaly detection.
Broader integration work remains Issue 18; financial-rule documentation remains
Issue 17. The P3 Streamlit chart-sizing deprecation stays deferred.
