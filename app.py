import sys
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent / "src"))

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
        repository.add_goal(FinancialGoal(name, target_amount, saved_amount, deadline, priority))
        st.success("Goal saved.")
        st.rerun()

st.subheader("Goals")
goals = repository.list_goals()
if not goals:
    st.info("You have no goals yet.")
for goal in goals:
    st.write(f"**{goal.name}** · {goal.saved_amount:.2f} / {goal.target_amount:.2f} EUR")
    st.progress(goal.progress)

st.subheader(f"Transactions for {month}")
if transactions:
    st.dataframe([
        {"Date": item.transaction_date.isoformat(), "Type": "Income" if item.transaction_type == "income" else "Expense", "Amount": f"{item.amount:.2f} EUR", "Category": item.category, "Description": item.description}
        for item in transactions
    ], use_container_width=True, hide_index=True)
else:
    st.info("There are no transactions for this month.")