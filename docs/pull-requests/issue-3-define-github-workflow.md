# PR: Define the GitHub workflow

## Summary

Closes #3 by adding a beginner-friendly workflow guide and a reusable PR checklist. The permanent roles remain defined in `AGENTS.md`.

## Scope

- Adds `.github/pull_request_template.md`.
- Adds `docs/github-workflow.md` and links it from `README.md`.
- Records Issue #3 implementation and this PR summary.
- Excludes existing uncommitted `.github/copilot-instructions.md` edits.

## Validation

- Diff reviewed against Issue #3 acceptance criteria.
- Local Markdown links in all five changed files resolve; whitespace checks passed.
- `.venv` Python: `python -m pytest -q` passed (3 tests).
- `.venv` Python: `python -m ruff check app.py main.py src tests` passed.
- Preserved instruction file SHA256: `551EA10B82261A7D8B161A47B8390FDBCA2465EED1A1BE1C2AD94E0148AC796B`.

No new automated tests are needed for these documentation/template changes. GitHub's automatic template rendering still requires confirmation in the web PR creation UI.

## Review status

Pending independent Senior Engineer review. No approval or merge is claimed.
