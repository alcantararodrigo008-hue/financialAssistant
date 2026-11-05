# Issue 15: Make guidance thresholds configurable

Source: [GitHub Issue #15](https://github.com/alcantararodrigo008-hue/financialAssistant/issues/15).

| Requirement | Implementation / evidence |
| --- | --- |
| Define thresholds in a configuration object or file | Immutable, validated `GuidanceConfig` and `DEFAULT_GUIDANCE_CONFIG` in their own module |
| Pass configuration into recommendation rules | Optional keyword argument preserves existing Python callers; application passes defaults explicitly |
| Document each threshold, meaning and defaults | [Configuration guide](../guidance-configuration.md): percentage units, 10% savings / 40% category defaults, strict comparisons, ranges, examples and restart instructions |
| No hidden magic thresholds | Rule comparisons and explanation text both use configuration fields |
| Changing configuration changes behavior without interface edits | Unit and AppTest cases change percentages and check both triggers and displayed explanations with unchanged metrics and records |

Depends on Issue #14's pure guidance module and existing exact Decimal summary.
No new dependency, schema, persistent setting, settings UI, financial rule or model
change. Goal and emergency-fund behavior remain unchanged. Configurable financial
thresholds are distinct from 100, the fixed percentage-unit conversion factor.

Regression coverage includes default compatibility, strict/fractional boundaries,
0/100 endpoints, invalid field values, bypassed frozen fields, hostile Decimal
settings, large amounts, deficit precedence, missing records/income, actual
application reruns, month/filter isolation, invalid submissions and reopening.
Invalid settings cannot silently produce guidance or modify stored records.
The existing P3 Streamlit chart-sizing deprecation remains deferred.
