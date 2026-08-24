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