# Issue 4: Create the folder structure

Source: [Issue #4](https://github.com/alcantararodrigo008-hue/financialAssistant/issues/4).

## Requirements and implementation

- Preserve `app.py`, `main.py`, dependencies, plan, and the existing package, docs, and tests.
- Track `data/.gitkeep` so a fresh checkout includes the data directory.
- Ignore all local data contents except that placeholder, including SQLite sidecars.
- Configure pytest to import `financial_assistant` from `src/`, matching the app's package name. Previously the standalone pytest launcher failed with `No module named src`.
- Document the layout and repository-root launch requirement.
- Exercise actual Streamlit script execution and SQLite initialization in a temporary directory, without touching user data.

## Review status

Ready for independent review after recorded validation; no approval or issue closure is claimed.
