# Issue 1: Configure the Python environment

## Objective

Prepare a reproducible environment for running, testing, and maintaining the local financial assistant.

## Tasks

- [x] Crear `requirements.txt`.
- [x] Add Streamlit as an application dependency.
- [x] Add pytest for automated tests.
- [x] Add Ruff for formatting and linting.
- [x] Create `.gitignore` rules for Python, VS Code, SQLite, and local files.
- [x] Document virtual environment creation and activation.
- [x] Document dependency installation and Streamlit startup.

## Acceptance criteria

- A user can create a virtual environment with Python 3.12 or newer.
- Dependencies install with `python -m pip install -r requirements.txt`.
- The application starts with `streamlit run app.py`.
- Tests run with `pytest`.
- Local database files are not included in Git.
- Ruff checks pass without errors.

## Validation

- `pytest -q`: 3 tests passed.
- `ruff check app.py main.py src tests`: no errors.
- Streamlit starts successfully at `http://localhost:8501`.

## Notes

This project is educational. It does not provide professional financial advice or investment recommendations.
