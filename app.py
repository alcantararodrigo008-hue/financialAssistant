import sys
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent / "src"))

from financial_assistant.goal_planning import required_monthly_savings
from financial_assistant.models import CATEGORIES, FinancialGoal, Transaction
from financial_assistant.repository import SQLiteRepository

repository = SQLiteRepository()
st.set_page_config(page_title="Financial Assistant", page_icon="€", layout="wide")
st.title("Financial Assistant")
st.caption("Your data is stored locally. Educational project, not financial advice.")

today = datetime.now(timezone.utc).date()
month = st.sidebar.date_input("Dashboard month", today, key="dashboard_month").strftime("%Y-%m")
transactions = repository.list_transactions(month)
income = sum(item.amount for item in transactions if item.transaction_type == "income")
expenses = sum(item.amount for item in transactions if item.transaction_type == "expense")
savings = income - expenses

metric_columns = st.columns(4)
metric_columns[0].metric("Income", f"{income:.2f} EUR")
metric_columns[1].metric("Expenses", f"{expenses:.2f} EUR")
metric_columns[2].metric("Net savings", f"{savings:.2f} EUR")
metric_columns[3].metric("Savings rate", f"{(savings / income * 100):.1f}%" if income else "No income")

with st.expander("Add transaction", expanded=True), st.form("transaction_form"):
        columns = st.columns(3)
        transaction_type = columns[0].selectbox("Type", ["income", "expense"], format_func=lambda value: "Income" if value == "income" else "Expense")
        amount = columns[1].number_input("Amount (EUR)", min_value=0.01, step=10.0)
        transaction_date = columns[2].date_input("Date", today)
        category = st.selectbox("Category", sorted(CATEGORIES))
        description = st.text_input("Description")
        recurring = st.checkbox("Recurring transaction")
        if st.form_submit_button("Guardar movimiento"):
            repository.add_transaction(Transaction(transaction_type, amount, transaction_date, category, description, recurring))
            st.success("Transaction saved.")
            st.rerun()

with st.expander("Create goal"), st.form("goal_form"):
    name = st.text_input("Goal name")
    target_amount = st.number_input("Target amount (EUR)", min_value=0.01, step=100.0)
    saved_amount = st.number_input("Current savings (EUR)", min_value=0.0, step=50.0)
    deadline = st.date_input("Deadline (optional)", value=None)
    priority = st.number_input("Priority", min_value=1, max_value=5, value=1)
    if st.form_submit_button("Save goal"):
        try:
            goal = FinancialGoal(name, target_amount, saved_amount, deadline, priority)
        except ValueError as error:
            st.error(str(error))
        else:
            repository.add_goal(goal)
            st.session_state["goal_saved"] = True
            st.rerun()

if st.session_state.pop("goal_saved", False):
    st.success("Goal saved.")


def show_goal(goal: FinancialGoal) -> None:
    st.text(goal.name)
    st.caption(f"Priority: {goal.priority} | Saved: {goal.saved_amount:.2f} / {goal.target_amount:.2f} EUR")
    st.progress(goal.progress, text=f"Progress: {goal.progress:.1%}")
    if goal.status == "completed":
        st.info("Marked completed. No further monthly saving is planned.")
    elif goal.saved_amount >= goal.target_amount:
        st.success("Goal reached! Your savings cover the target.")
    elif goal.deadline is None:
        st.info("No deadline. Save at your own pace; no monthly estimate is set.")
    elif goal.deadline < today:
        st.warning(f"Deadline passed ({goal.deadline.isoformat()}). Review the deadline or remaining amount.")
    elif goal.deadline == today:
        st.warning("Due today. The remaining amount is due now; no monthly estimate applies.")
    else:
        monthly = required_monthly_savings(goal, today)
        st.write(f"Required monthly savings (estimate): {monthly:.2f} EUR")
        st.caption(f"Deadline: {goal.deadline.isoformat()} | Partial calendar months count as a full month; rounded up to cents.")


st.subheader("Active goals")
goals = repository.list_goals()
active_goals = [goal for goal in goals if goal.status == "active"]
if not active_goals:
    st.info("You have no active goals yet. Create one above.")
for goal in active_goals:
    show_goal(goal)
completed_goals = [goal for goal in goals if goal.status == "completed"]
if completed_goals:
    with st.expander("Completed goals"):
        for goal in completed_goals:
            show_goal(goal)

st.subheader(f"Transactions for {month}")
if transactions:
    st.dataframe([
        {"Date": item.transaction_date.isoformat(), "Type": "Income" if item.transaction_type == "income" else "Expense", "Amount": f"{item.amount:.2f} EUR", "Category": item.category, "Description": item.description}
        for item in transactions
    ], use_container_width=True, hide_index=True)
else:
    st.info("There are no transactions for this month.")
