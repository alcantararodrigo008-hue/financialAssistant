import sys
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent / "src"))

from financial_assistant.goal_planning import required_monthly_savings
from financial_assistant.models import CATEGORIES, FinancialGoal, Transaction
from financial_assistant.monthly_summary import calculate_monthly_summary
from financial_assistant.repository import SQLiteRepository
from financial_assistant.visualizations import (
    ChartRangeError,
    daily_trends_spec,
    expense_distribution_spec,
)

repository = SQLiteRepository()
st.set_page_config(page_title="Financial Assistant", page_icon="€", layout="wide")
st.title("Financial Assistant")
st.caption("Your data is stored locally. Educational project, not financial advice.")

today = datetime.now(timezone.utc).date()
selected_month = st.sidebar.date_input("Dashboard month", today, key="dashboard_month")
if selected_month is None:
    st.info("Choose a dashboard month to record and view transactions.")
    st.stop()
month = selected_month.strftime("%Y-%m")
transactions = repository.list_transactions(month)
summary = calculate_monthly_summary(transactions)

st.subheader(f"Monthly summary for {month}")
metric_columns = st.columns(4)
metric_columns[0].metric("Income", f"{summary.income:.2f} EUR")
metric_columns[1].metric("Expenses", f"{summary.expenses:.2f} EUR")
metric_columns[2].metric("Net savings", f"{summary.net_savings:.2f} EUR")
metric_columns[3].metric("Savings rate", f"{summary.savings_rate_percent:.1f}%" if summary.savings_rate_percent is not None else "No income")
st.caption("Net savings = income minus expenses. Savings rate = net savings / income × 100; unavailable without income.")


def show_transaction_chart(title, builder, key, empty_message):
    st.subheader(title)
    try:
        spec = builder(transactions)
    except ChartRangeError:
        st.info("These amounts exceed the chart's exact numeric range. Use the exact dashboard metrics and transaction records instead.")
    else:
        if spec is None:
            st.info(empty_message)
        else:
            st.vega_lite_chart(spec=spec, use_container_width=True, key=key)


st.caption("Charts use the same selected-month records as the metrics. Hover or tap for exact EUR amounts; axes use compact units (k, M).")
show_transaction_chart("Expenses by category", expense_distribution_spec, "expense_distribution",
                       "No expenses this month. Add an expense or choose another dashboard month.")
show_transaction_chart("Daily income, expenses, and net savings", daily_trends_spec, "daily_trends",
                       "No transactions this month. Add income or an expense to start the daily trend.")
st.caption("Daily totals are not cumulative. Only recorded dates are plotted; gaps connect observations and do not imply missing dates had transactions.")
if len({item.transaction_date for item in transactions}) == 1:
    st.info("Only one recorded day this month: points show that day's totals. Add transactions on more dates to see a trend.")

with st.expander("Add transaction", expanded=True), st.form("transaction_form"):
    columns = st.columns(3)
    transaction_type = columns[0].selectbox("Type", ["income", "expense"], format_func=lambda value: "Income" if value == "income" else "Expense")
    amount = columns[1].text_input("Amount (EUR)", value=None, placeholder="e.g. 12.50", help="Required. Enter a positive decimal amount using a dot; no currency symbols or commas.")
    transaction_date = columns[2].date_input("Date", today)
    category = st.selectbox("Category", sorted(CATEGORIES))
    description = st.text_input("Description (optional)")
    recurring = st.checkbox("Recurring transaction")
    if st.form_submit_button("Save transaction"):
        try:
            transaction = Transaction(transaction_type, amount, transaction_date, category, description, recurring)
        except ValueError as error:
            st.error(str(error))
        else:
            repository.add_transaction(transaction)
            st.session_state["transaction_saved"] = True
            st.rerun()

if st.session_state.pop("transaction_saved", False):
    st.success("Transaction saved.")

with st.expander("Create goal"), st.form("goal_form"):
    name = st.text_input("Goal name")
    target_amount = st.text_input("Target amount (EUR)", value=None, placeholder="e.g. 1000.00", help="Required. Enter a positive decimal target using a dot.")
    saved_amount = st.text_input("Current savings (EUR)", value=None, placeholder="Enter 0 if you have no savings", help="Required. Enter a nonnegative decimal amount using a dot. Zero is valid; blank is not zero.")
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
    if st.button("Delete goal", key=f"request_delete_goal_{goal.goal_id}"):
        st.session_state["pending_deletion"] = ("goal", goal)
        st.rerun()


st.subheader("Active goals")
st.caption("Goal progress shows current saved balances, capped at 100%, independent of the transaction month. Goal balances are not historical monthly snapshots.")
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
st.caption("Choose the month using Dashboard month in the sidebar. Records are shown newest first.")
filter_columns = st.columns(2)
type_filter = filter_columns[0].selectbox(
    "Transaction type filter", [None, "income", "expense"], key="transaction_type_filter",
    format_func=lambda value: "All types" if value is None else value.title(),
)
category_filter = filter_columns[1].selectbox(
    "Transaction category filter", [None, *sorted(CATEGORIES)], key="transaction_category_filter",
    format_func=lambda value: "All categories" if value is None else value,
)
filtered_transactions = repository.list_transactions(month, type_filter, category_filter)
st.caption("These list filters do not change the monthly dashboard totals.")
if filtered_transactions:
    st.dataframe([
        {"Date": item.transaction_date.isoformat(), "Type": "Income" if item.transaction_type == "income" else "Expense", "Amount": f"{item.amount:.2f} EUR", "Category": item.category, "Description": item.description, "Recurring": item.recurring}
        for item in filtered_transactions
    ], use_container_width=True, hide_index=True)
else:
    st.info("No transactions match the selected month, type, and category. Add a transaction above, choose another month, or select All types and All categories.")

if filtered_transactions:
    transaction_options = {item.transaction_id: item for item in filtered_transactions}
    if st.session_state.get("transaction_to_delete") not in transaction_options:
        st.session_state["transaction_to_delete"] = None
    deletion_id = st.selectbox(
        "Transaction to delete", [None, *transaction_options], key="transaction_to_delete",
        format_func=lambda value: "Choose a transaction" if value is None else (
            f"#{value} | {transaction_options[value].transaction_date.isoformat()} | "
            f"{transaction_options[value].transaction_type.title()} | {transaction_options[value].amount:.2f} EUR | "
            f"{transaction_options[value].category}"
        ),
    )
    if st.button("Delete transaction", disabled=deletion_id is None):
        st.session_state["pending_deletion"] = ("transaction", transaction_options[deletion_id])
        st.rerun()

if message := st.session_state.pop("deletion_message", None):
    st.info(message)

if pending := st.session_state.get("pending_deletion"):
    kind, record = pending
    st.warning(f"Permanently delete this {kind}? This cannot be undone. Confirm or cancel below.")
    if kind == "goal":
        st.text(f"Goal #{record.goal_id}: {record.name}\nSaved: {record.saved_amount:.2f} / {record.target_amount:.2f} EUR")
    else:
        st.text(f"Transaction #{record.transaction_id}: {record.transaction_date.isoformat()} | {record.transaction_type} | {record.amount:.2f} EUR | {record.category}\n{record.description}")
    confirm_column, cancel_column = st.columns(2)
    if confirm_column.button("Confirm delete", key="confirm_deletion"):
        if kind == "goal":
            deleted = repository.delete_goal(record.goal_id, expected=record)
        else:
            deleted = repository.delete_transaction(record.transaction_id, expected=record)
        st.session_state.pop("pending_deletion")
        st.session_state["deletion_message"] = (
            "Record deleted." if deleted else "Record changed or was already deleted. Nothing was deleted; select the record again if needed."
        )
        st.rerun()
    if cancel_column.button("Cancel deletion", key="cancel_deletion"):
        st.session_state.pop("pending_deletion")
        st.session_state["deletion_message"] = "Deletion cancelled. Your records were kept."
        st.rerun()
