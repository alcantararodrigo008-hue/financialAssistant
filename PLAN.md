# Financial Assistant Prototype Plan

## Objective

Build a local web application that helps a person identify and prioritize financial goals, record income and expenses, understand their monthly situation, estimate required savings, and receive simple, explainable suggestions.

The project initially supports one user and uses Python, Streamlit, and SQLite. It is also a practical project for learning GitHub, GitHub Copilot, and Visual Studio Code.

> This project is educational. It does not replace professional financial advice and the MVP does not provide investment recommendations.

## Initial decisions

- **Interface:** local Streamlit web application.
- **Language:** Python.
- **Storage:** local SQLite database.
- **Users:** one user.
- **Guidance:** transparent rules about budgets, savings, and goals.
- **Privacy:** data stays local and does not connect to bank accounts.

## MVP scope

### Financial goals

Each goal includes a name, target amount, current savings, optional deadline, priority, and active or completed status. The application shows progress and calculates approximate monthly savings required when a deadline exists.

### Income and expenses

Each transaction includes a type, positive amount, date, category, optional description, and recurring or one-time indicator.

Initial categories: Housing, Food, Transport, Health, Leisure, Education, Debt, Savings, and Other.

### Dashboard

The monthly dashboard shows total income, total expenses, net savings, savings rate, expenses by category, monthly trends, and active goal progress.

Initial formulas:

- `net savings = income - expenses`
- `savings rate = net savings / income` when income is greater than zero.
- `required monthly savings = remaining amount / remaining months`

The application explicitly handles missing data, deficit months, overdue goals, and completed goals.

## Milestones and issues

## Milestone 1: Prepare the project

### Issue 1. Configure the Python environment

- Create `requirements.txt` or `pyproject.toml`.
- Add Streamlit, pytest, and formatting or linting tools.
- Create `.gitignore` rules for Python, VS Code, SQLite, and local files.
- Document virtual environment creation, installation, and execution.

### Issue 2. Create initial documentation

- Explain the project objective in `README.md`.
- Add installation and execution instructions.
- Document the educational nature and financial limitations.

### Issue 3. Define the GitHub workflow

- Create one branch per issue.
- Keep pull requests small.
- Use clear commit messages such as `feat: add expense registration`.
- Create a pull request template with a checklist.
- Practice code review before merging.

### Issue 4. Create the folder structure

Use `app.py`, `main.py`, `requirements.txt`, `README.md`, `PLAN.md`, `data/`, `docs/`, `src/financial_assistant/`, and `tests/`. The local database inside `data/` must not be committed.

## Milestone 2: Model the data

### Issue 5. Create domain models

Implement `FinancialGoal` and `Transaction` with validation for positive amounts, valid dates, allowed transaction types, allowed categories, and allowed goal statuses.

### Issue 6. Implement SQLite persistence

Create a module that initializes tables automatically, supports CRUD operations for goals and transactions, filters transactions by month, type, and category, and keeps SQL details out of the interface.

### Issue 7. Test models and repositories

Test creating and retrieving records, rejecting invalid amounts, filtering by month, and calculating income, expenses, and savings correctly.

## Milestone 3: Register information

### Issue 8. Create the goals screen

Add goal creation, active goal display, visual progress, required monthly savings, and reached-goal messages.

### Issue 9. Create the transactions screen

Add income and expense forms, category and date selection, optional descriptions, recent transactions, and filters by month, type, and category.

### Issue 10. Add interface validation

Reject negative or zero amounts, show understandable errors, confirm before deletion, and design empty states for missing records.

## Milestone 4: Build the dashboard

### Issue 11. Add the monthly summary

Show the selected month's metrics and recalculate them after every transaction.

### Issue 12. Add visualizations

Add readable expense distribution, income/expense/savings trends, and goal progress visualizations when enough data exists.

### Issue 13. Handle edge cases

Verify behavior with no income, no expenses, expenses above income, passed deadlines, goals without deadlines, and completed goals.

## Milestone 5: Add financial guidance

### Issue 14. Implement explainable rules

Create an independent recommendations module. Explain each suggestion and cover monthly deficits, low savings rates, unusually high categories, potentially unreachable goals, and optional emergency fund goals.

Rules must not recommend automatic cuts to basic needs or investments.

### Issue 15. Make thresholds configurable

Store rule thresholds in configuration instead of hiding them in the interface or hard-to-change functions.

### Issue 16. Test recommendations

Cover monthly deficits, low savings rates, unusually high category spending, unreachable goals, missing data, and missing emergency funds.

## Milestone 6: Quality and documentation

### Issue 17. Document financial rules

Create `docs/financial-rules.md` with formulas, configurable thresholds, assumptions, examples, limitations, and risks.

### Issue 18. Add integration tests

Test the complete flow: create a goal, record income and expenses, open the dashboard, and verify progress and recommendations.

### Issue 19. Review privacy and security

Keep the database out of Git, avoid credentials and secrets, send no data to external services, avoid real banking data during testing, and explain limitations clearly.

### Issue 20. Prepare a demonstrable version

Review the README, optionally add demo data, run all tests, check the application manually, and open a final MVP pull request.

## Recommended implementation order

1. Configure the environment and `.gitignore`.
2. Complete `README.md` and the folder structure.
3. Implement models and validation.
4. Implement SQLite and repository tests.
5. Implement goals.
6. Implement income and expenses.
7. Implement dashboard calculations.
8. Implement guidance rules.
9. Integrate the Streamlit interface.
10. Add integration tests and document limitations.

## MVP acceptance criteria

- A user can create, edit, and delete goals.
- A user can record income and expenses.
- Data persists after restarting the application.
- The dashboard calculates selected-month totals correctly.
- Goal progress is visible.
- Recommendations explain why they appear.
- Empty and deficit states do not produce errors.
- Core logic has automated tests.
- Documentation explains installation, execution, and limitations.
- The repository contains no local database or secrets.
