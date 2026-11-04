# Financial Assistant

For development and pull requests, see the [GitHub workflow](docs/github-workflow.md).

Local web application for recording income and expenses, tracking savings goals, and understanding monthly finances. Data is stored in SQLite inside `data/` and the application does not connect to bank accounts.

## Run

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
