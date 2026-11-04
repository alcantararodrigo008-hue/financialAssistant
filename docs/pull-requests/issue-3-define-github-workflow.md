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

No new automated tests are needed for these documentation/template changes. Follow-up validation checked the discovery guidance against GitHub's documentation, local Markdown links, whitespace, and the preserved instruction-file checksum.

## Template discovery limitation and fallback

GitHub discovers templates from the default branch, currently `issue-1-configure-python-environment`, not `main`. Automatic discovery of this template is currently unavailable under the existing configuration; merging it into `main` alone will not populate new PR descriptions. This is a configuration limitation, not merely untested behavior.

Open `.github/pull_request_template.md`, copy its contents into the actual GitHub PR description, replace placeholders with real information, and complete the checklist before requesting review. The workflow guide documents these steps. No repository settings are changed.

## Review status

Pending independent Senior Engineer review. No approval or merge is claimed.
