from dataclasses import replace
from datetime import date, timedelta
from decimal import Decimal, Inexact, localcontext
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from financial_assistant.models import FinancialGoal, Transaction
from financial_assistant.recommendations import recommendations
from financial_assistant.repository import SQLiteRepository

TODAY = date(2024, 1, 15)
FUND = FinancialGoal('Emergency fund', 100)


def tx(kind, amount, category='Other'):
    return Transaction(kind, amount, TODAY, category)


def codes(records=(), goals=(FUND,)):
    return [r.code for r in recommendations(records, goals, as_of=TODAY)]


@pytest.mark.parametrize('income,expense,expected', [
    ('100', '90', False), ('100', '90.01', True), ('100', '89.99', False),
    ('1000', '900.01', True), ('100', '100', True),
])
def test_exact_low_savings_boundary(income, expense, expected):
    assert ('low_savings' in codes([tx('income', income), tx('expense', expense)])) == expected


@pytest.mark.parametrize('food,other,expected', [('40', '60', False), ('40.01', '59.99', True)])
def test_exact_category_threshold(food, other, expected):
    result = recommendations([tx('expense', food, 'Food'), tx('expense', other)], [FUND], as_of=TODAY)
    assert any(r.code == 'category_share' and r.explanation.startswith('Food ') for r in result) == expected
    assert 'low_savings' not in [r.code for r in result]


def test_missing_income_and_data_and_fund_name_convention():
    assert codes() == []
    assert codes(goals=[]) == ['emergency_fund']
    assert codes(goals=[replace(FUND, name='  EMERGENCY   fund ')]) == []
    assert codes(goals=[replace(FUND, name='Holiday')]) == ['emergency_fund']
    result = codes([tx('expense', '0.01')])
    assert result == ['deficit', 'category_share']


@pytest.mark.parametrize('offset,expected', [(-1, 'goal_deadline'), (0, 'goal_deadline'), (31, 'goal_capacity')])
def test_goal_alternatives(offset, expected):
    goal = FinancialGoal('Trip', '100', deadline=TODAY + timedelta(days=offset))
    result = recommendations([tx('income', '10')], [FUND, goal], as_of=TODAY)
    suggestion = next(r for r in result if r.code == expected)
    assert 'deadline' in suggestion.explanation
    assert 'target' in suggestion.explanation
    assert '100.00 EUR' in suggestion.explanation or expected == 'goal_capacity'


def test_goal_capacity_equal_missing_data_and_exclusions():
    goal = FinancialGoal('Trip', '100', deadline=date(2024, 2, 15))
    assert 'goal_capacity' not in codes([tx('income', '100')], [FUND, goal])
    assert 'goal_capacity' in codes([tx('income', '99.99')], [FUND, goal])
    assert codes([], [FUND, goal]) == []  # Missing data is not a zero-income forecast.
    for skipped in [replace(goal, status='completed'), replace(goal, saved_amount=100), replace(goal, deadline=None)]:
        assert codes([tx('expense', '1')], [FUND, skipped]) == ['deficit', 'category_share']


def test_deterministic_context_independent_and_does_not_mutate():
    records = [tx('income', '99999999999999999999999999.99'), tx('expense', '99999999999999999999999999.98')]
    goals = [FUND, FinancialGoal('Trip', '100', deadline=date(2024, 2, 15))]
    expected = recommendations(records, goals, as_of=TODAY)
    with localcontext() as ctx:
        ctx.prec = 3
        ctx.traps[Inexact] = True
        assert recommendations(iter(records), iter(goals), as_of=TODAY) == expected
    assert records[0].amount == Decimal('99999999999999999999999999.99')


@pytest.mark.parametrize('kind', ['date', 'goal_type', 'transaction_type', 'goal_amount', 'transaction_amount'])
def test_invalid_inputs_rejected(kind):
    goals, records, day = [FUND], [tx('income', '10')], TODAY
    if kind == 'date':
        day = '2024-01-15'
    elif kind == 'goal_type':
        goals = [object()]
    elif kind == 'transaction_type':
        records = [object()]
    elif kind == 'goal_amount':
        goals = [replace(FUND)]
        object.__setattr__(goals[0], 'saved_amount', Decimal('NaN'))
    else:
        object.__setattr__(records[0], 'amount', Decimal('NaN'))
    with pytest.raises((ValueError, TypeError)):
        recommendations(records, goals, as_of=day)


def test_app_zero_one_multiple_guidance_and_reopening(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    repo = SQLiteRepository()
    path = str(Path(__file__).resolve().parents[1] / 'app.py')
    app = AppTest.from_file(path, default_timeout=10).run()
    assert any("No goal named 'Emergency fund'" in item.value for item in app.text)
    fund_id = repo.add_goal(FUND)
    app.run()
    assert any('No guidance rules triggered' in item.value for item in app.info)
    # Only the selected month contributes, regardless of list filters.
    repo.add_transaction(tx('income', '100'))
    repo.add_transaction(tx('expense', '125', 'Food'))
    repo.add_transaction(replace(tx('income', '9999'), transaction_date=date(2024, 2, 1)))
    repo.add_goal(FinancialGoal('Trip', '100', deadline=date(2020, 1, 1)))
    original = repo.list_transactions(), repo.list_goals()
    def check(rendered):
        assert not rendered.exception
        texts = [item.value for item in rendered.text]
        assert any('exceed income by 25.00 EUR' in t for t in texts)
        assert any('Food accounts for 125.00 EUR' in t for t in texts)
        assert any('original deadline' in t for t in texts)
        assert not any("No goal named 'Emergency fund'" in t for t in texts)
        assert (repo.list_transactions(), repo.list_goals()) == original
    app.date_input(key='dashboard_month').set_value(TODAY).run()
    check(app)
    app.selectbox(key='transaction_type_filter').select('income').run()
    check(app)
    reopened = AppTest.from_file(path, default_timeout=10).run()
    reopened.date_input(key='dashboard_month').set_value(TODAY).run()
    check(reopened)
    assert repo.get_goal(fund_id).name == 'Emergency fund'
