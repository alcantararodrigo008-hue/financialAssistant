# Pull Request: Configure the Python environment

## Summary

Closes issue #1 by documenting and validating the reproducible Python environment
for the Financial Assistant MVP.

## Changes

- Declares Streamlit, pytest, and Ruff in `requirements.txt`.
- Documents Python 3.12 or newer, virtual environment setup, installation, and
  application startup in `README.md`.
- Adds Python, VS Code, SQLite, virtual environment, cache, and local installer
  exclusions to `.gitignore`.

## Validation

- `python -m pytest -q`: 3 tests passed.
- `python -m ruff check app.py main.py src tests`: passed.
- `python -m streamlit run app.py --server.headless true --server.port 8502`:
  application started successfully.
- Local `.msix` installer is ignored by Git.

## Review checklist

- [x] The application dependency is documented.
- [x] Automated testing dependency is documented.
- [x] Formatting and linting dependency is documented.
- [x] Setup and execution instructions are documented.
- [x] Local databases, environments, caches, and installers are excluded.
- [x] Tests and lint checks pass.

## Review decision

**Approved after follow-up changes.**

The PowerShell activation command in `README.md` was corrected to
`.\.venv\Scripts\Activate.ps1` and the embedded NUL byte was removed. The
README now renders as text and the setup command works as documented.

Follow-up validation confirmed that the test suite passes with 3 tests and
Ruff reports no errors. The pull request is mergeable with no conflicts. No
automated GitHub checks are configured, so the decision is based on the local
validation recorded above.

## Merge

Merged into `main` on August 24, 2026, as commit `8205417`
(`82054171a7d283bf14c18e2ea4f74ccfa9dbead5`).