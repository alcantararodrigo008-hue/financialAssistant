# Financial Assistant

For development and pull requests, see the [GitHub workflow](docs/github-workflow.md).
For storage methods, filters, and privacy boundaries, see [SQLite persistence](docs/sqlite-persistence.md).
For goal creation, progress, and savings estimate assumptions, see [the goals screen](docs/goals-screen.md).
For recommendation thresholds, defaults, and customization, see [guidance configuration](docs/guidance-configuration.md).

Local web application for recording income and expenses, tracking savings goals, and understanding monthly finances. Data is stored in SQLite inside `data/` and the application does not connect to bank accounts.

## Run

Run the commands below from the repository root. The repository uses this structure:

```text
app.py                    Streamlit application entry point
main.py                   Prints the command for launching the app
requirements.txt          Application and development dependencies
pytest.ini                Test discovery and src package import configuration
README.md / PLAN.md       Setup guide and project plan
data/                     Local data; only .gitkeep is tracked
docs/                     Workflow, issue notes, and PR notes
src/financial_assistant/  Python package: models and SQLite repository
tests/                    Automated model, repository, and app smoke tests
```

The app loads its package from `src/`; pytest uses the same package through
`pytest.ini`. No editable installation or external `PYTHONPATH` is required for
these entry points. A standalone Python shell must add `src/` to its import path.
The repository creates `data/financial_assistant.db` relative to the current
working directory when the app runs. All contents of the root `data/` directory
except `.gitkeep` are ignored, including SQLite databases and journal/WAL files.
Keep local databases in that directory; Git does not ignore arbitrary database
paths elsewhere in the repository.

Requires Python 3.12 or newer.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run app.py
```

The application will open at `http://localhost:8501`.

To run the tests:

```powershell
pytest
```

To check the code with Ruff:

```powershell
python -m ruff check app.py main.py src tests
```

This is an educational project. Its calculations and suggestions do not replace professional financial advice, and the MVP does not provide investment recommendations.
