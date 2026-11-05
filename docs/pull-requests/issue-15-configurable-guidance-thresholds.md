# PR: Configurable guidance thresholds

Closes #15.

Move the existing savings/category thresholds to an immutable, validated
configuration object. Rules and explanation text consume that object, and the app
passes the default configuration explicitly. Defaults remain 10% / 40%, preserving
existing guidance behavior. See the [configuration guide](../guidance-configuration.md)
and [Issue 15 notes](../issues/milestone-5-issue-15-configurable-guidance-thresholds.md).

## Validation

- `pytest -q -p no:cacheprovider`: 354 passed (129.15s).
- `python -B -m pytest -q -p no:cacheprovider`: 354 passed (115.16s).
  52 new cases cover custom/default settings, strict fractional boundaries, 0/100,
  malformed/nonfinite/range/precision errors, immutable/bypassed configurations,
  hostile Decimal contexts and large monetary values.
- Ruff (`check --no-cache app.py main.py src tests`) passed; `pip check` found no
  broken requirements. Local Markdown links passed across 41 documents; staged,
  working-tree and full issue diff whitespace checks passed. Only data/.gitkeep is
  tracked; databases, sidecars and nested private data remain ignored.
- AppTest regression covers explicit config injection without interface edits,
  matching explanations, unchanged metrics/records, December–January selection,
  list-filter isolation, invalid submissions and reopened persistence. A separate
  actual-submission probe verifies valid saves persist exactly once, reruns do not
  duplicate records, and confirmed deletion refreshes guidance under custom settings.
- A 1,000-case integer-cent/custom-percentage oracle passed, including large money
  and caller contexts with low precision and all Decimal traps enabled.
- Real headless Edge at 1366x900 and 390x844 verified injected 25.5% / 80% settings:
  updated savings guidance, suppressed category prompts, accurate metrics, both
  charts, no horizontal document overflow or uncaught JavaScript exceptions.
  Synthetic database records unchanged; temporary server/browser stopped.
- Complete implementation/test/documentation diff reviewed for threshold/label
  consistency, precision, invalid inputs, scope, privacy and data integrity.
- Existing .github/copilot-instructions.md excluded and unchanged; before/after
  SHA256: 551EA10B82261A7D8B161A47B8390FDBCA2465EED1A1BE1C2AD94E0148AC796B.
  All pre-existing branches retained.

## Scope and limitations

Configuration is a Python object; changing application defaults requires a process
restart, not interface changes. No runtime settings UI, external file, schema or
database configuration storage. Percentages support 0–100 and up to 28 decimal
places; malformed/invalid settings fail clearly instead of silently falling back.
Existing goal/emergency-fund heuristics, UTC dates, monthly selection and privacy
boundaries remain. No automatic allocation, basic-needs cuts or investments.
P3 chart-sizing deprecation remains deferred. Other browsers/devices, accessibility,
load/concurrency, fresh dependency installs and minimum versions are not verified.

Preserve pre-existing instruction edits and all branches. Target main; the GitHub
default branch differs, so use a manually populated PR description and do not
assume closing keywords automatically close the issue. Stop for Chat 2 independent
review; no developer approval, final Senior comment or merge.
