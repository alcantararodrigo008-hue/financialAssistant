# Financial Assistant

A local, single-user educational prototype for recording income and expenses,
tracking goals, understanding a selected month and reading explainable guidance.
It uses Streamlit and SQLite, with no bank connections or investment advice.

## Install and run (Windows PowerShell)

You need Git and Python 3.12 or newer. Internet access is needed to clone the
repository and install dependencies, not to connect financial accounts. Open
PowerShell in a private parent folder outside OneDrive or other cloud syncing.
Use a **new directory name** for a clean demo; do not overwrite an existing checkout
or delete its database to follow these steps.

```powershell
git clone --branch main https://github.com/alcantararodrigo008-hue/financialAssistant.git financial-assistant-demo
Set-Location financial-assistant-demo
python --version
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Check that `python --version` reports 3.12 or newer before creating the environment.
These commands use the environment's executable directly: activation and changes
to PowerShell execution policy are unnecessary. `--branch main` is deliberate;
the repository's current GitHub default branch differs from `main`.

Run from the repository root so [.streamlit/config.toml](.streamlit/config.toml)
applies. Open `http://127.0.0.1:8501` while the terminal stays running. Stop with
Ctrl+C; rerun the same launch command to reopen saved data. If port 8501 is busy,
stop your other demo process or append `--server.port=8502` and open that local port.
For `python` not found or an older version, install/select Python 3.12+ before
continuing; do not fall back to an unrelated global Streamlit installation.

The root launch defaults bind to IPv4 loopback and disable Streamlit usage
statistics. No account or credentials are required for the financial flow. Use
**synthetic data only**: the app does not encrypt SQLite files and cloud-synced
folders may upload them independently. See [privacy and security](docs/privacy-security.md)
for configuration overrides, storage and deployment limitations.

## Demonstrate the main flow

Follow the [clean-data demonstration](docs/demo-walkthrough.md) to create a goal,
record income/expenses, verify exact totals and progress, see explained suggestions,
check validation, confirm deletion and reopen persisted records. The walkthrough
uses manual forms and synthetic values; there is no automatic loader or reset.
A new clone starts without a database; normal launches preserve existing records.

## What works and what remains limited

- Create goals with manual saved balances, optional deadlines and priorities;
  show progress and required monthly saving estimates; confirm before deleting.
- Record income/expenses, dates, categories, descriptions and recurring metadata;
  filter lists and view monthly metrics, charts and explainable suggestions.
- Keep records in local SQLite across restarts. Transactions do not automatically
  fund goals; recurring metadata does not generate future transactions.
- Goal editing and completion-status controls are **not implemented in the UI**;
  update methods exist only in the Python repository API. This demonstrable
  prototype does not claim every broader capability listed in [PLAN.md](PLAN.md).
- Guidance is based on recorded data, one month and individual goals. It is not
  personalized advice, a forecast, investment guidance or an automatic allocation.
- No application encryption, authentication, secure erasure, bank reconciliation
  or production deployment protection. Do not expose the server publicly.

Known deferred follow-ups remain: Streamlit chart-sizing deprecation, optional
first-launch email documentation, and independent LAN-isolation/minimum-Streamlit
verification. This demonstration does not resolve or certify those areas.

## Validate

From the repository root, using the installed environment:

```powershell
.\.venv\Scripts\pytest.exe -q
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check app.py main.py src tests
.\.venv\Scripts\python.exe -m pip check
```

Tests use temporary SQLite files and synthetic data rather than existing user
records. Dependency declarations live in [requirements.txt](requirements.txt). Ruff is
pinned to the verified 0.16.4 for repeatable validation without unrelated style
migrations. Application dependencies are not a frozen lockfile or a claim that
every Python/Streamlit version was tested.
The command examples target Windows PowerShell; other platforms require their
normal environment executable paths and have not been verified here.

## Storage and project layout

```text
app.py                    Streamlit entry point
main.py                   Prints the launch command
requirements.txt          Application and test/lint dependencies
src/financial_assistant/  Validated models, repository and financial services
tests/                    Unit, persistence, UI, integration and privacy tests
data/                     Local records; only .gitkeep is tracked
docs/                     Guides, issue notes and pull-request notes
.streamlit/config.toml    Local launch privacy defaults
```

The database is `data/financial_assistant.db` relative to the launch working
directory. Missing tables are created automatically. Root `data/` contents except
`.gitkeep` are ignored, including exports and sidecars. Common SQLite extensions
are also ignored elsewhere, but arbitrary exports/extensionless files outside
`data/` are not automatically protected. Ignore rules do not untrack files or
protect data from OS/cloud syncing. Keep private financial files out of Git.

The app adds `src/` to its imports; pytest uses [pytest.ini](pytest.ini). Neither
entry point requires an editable installation or external `PYTHONPATH`. Standalone
Python scripts must add `src/` themselves.

## Further documentation

- [Financial formulas, rules, examples and risks](docs/financial-rules.md)
- [Guidance threshold defaults and customization](docs/guidance-configuration.md)
- [Goal progress and deadline assumptions](docs/goals-screen.md)
- [SQLite methods and transaction boundaries](docs/sqlite-persistence.md)
- [Privacy and security limitations](docs/privacy-security.md)
- [Developer and independent review workflow](docs/github-workflow.md)

This project is educational and does not replace professional financial advice.
