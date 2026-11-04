# PR: Create the folder structure

## Summary

Closes #4 by completing the existing layout, fixing pytest package discovery, and protecting local data files. Existing domain and repository behavior is retained.

## Validation plan

- Run both pytest entry points and Ruff.
- Run Streamlit AppTest against a temporary working directory and database.
- Verify Git ignore behavior for databases, SQLite sidecars, and nested local data; verify the placeholder remains trackable.
- Inspect the complete staged diff, Markdown links, and a fresh clone's layout and tests.
- Verify existing uncommitted instruction-file edits remain byte-for-byte unchanged and excluded.

Results and limitations are recorded in the actual GitHub PR description. No production financial data is used.

## Limitations

The app uses a working-directory-relative database path; launch from the repository root. AppTest executes the script but does not test browser rendering or an HTTP server. GitHub's default branch remains `issue-1-configure-python-environment`, so the template must be copied manually and closing keywords targeting `main` do not automatically close the issue. Settings are unchanged. Pending independent review; do not merge without user authorization.
