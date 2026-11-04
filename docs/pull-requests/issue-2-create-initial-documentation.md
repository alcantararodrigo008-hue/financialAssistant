# Pull Request: Create initial documentation

## Summary

Closes issue #2 by documenting the purpose of the Financial Assistant, the installation workflow, and the project’s educational and financial limitations.

## Changes

- Adds a clear project objective and scope to `README.md`.
- Documents Python 3.12+ setup and virtual environment creation.
- Explains dependency installation and local execution through Streamlit.
- Notes that the application stores data locally in SQLite and does not connect to bank accounts.
- Describes the project as educational and clarifies that it does not provide professional financial advice or investment recommendations.

## Validation

- README content includes the project goal and intended use.
- Setup instructions show how to create a virtual environment and install dependencies.
- Execution instructions specify `streamlit run app.py` for local startup.
- The educational and financial limitation disclaimer is present and visible.

## Review checklist

- [x] The project objective is documented.
- [x] Installation steps are documented.
- [x] Execution steps are documented.
- [x] Educational context is included.
- [x] Financial limitations and disclaimers are documented.
- [x] The documentation is readable and usable for onboarding.

## Review decision

**Approved after validation.**

The new documentation is sufficient to onboard a developer or reviewer to the project, explains the intended use of the app, and clearly sets expectations around its educational scope and financial limitations.

## Merge

Ready to merge into `main` after review.
