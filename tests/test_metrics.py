import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import date
from models import Transaction
from metrics import compute

_BASE = dict(ref_no="REF", closing_balance=10000.0)


def txn(d: str, narration: str = "UPI-TEST", withdrawal=None, deposit=None) -> Transaction:
    dt = date.fromisoformat(d)
    return Transaction(date=dt, value_date=dt, narration=narration,
                       withdrawal=withdrawal, deposit=deposit, **_BASE)


# ── Edge cases ────────────────────────────────────────────────────────────────

def test_empty():
    m = compute([])
    assert m.total_income == 0
    assert m.total_expenses == 0
    assert m.net_savings == 0
    assert m.savings_rate == 0.0
    assert m.by_category == {}
    assert m.monthly == []
    assert m.top_expenses == []


def test_single_deposit():
    t = txn("2026-05-01", deposit=10000)
    m = compute([(t, "Salary")])
    assert m.total_income == 10000
    assert m.total_expenses == 0
    assert m.net_savings == 10000
    assert m.savings_rate == 100.0
    assert m.by_category == {}


def test_single_withdrawal():
    t = txn("2026-05-01", withdrawal=500)
    m = compute([(t, "Food & Dining")])
    assert m.total_expenses == 500
    assert m.total_income == 0
    assert m.net_savings == -500
    assert m.by_category == {"Food & Dining": 500}


# ── Savings rate ──────────────────────────────────────────────────────────────

def test_savings_rate_positive():
    income = txn("2026-05-01", deposit=10000)
    expense = txn("2026-05-02", withdrawal=3000)
    m = compute([(income, "Salary"), (expense, "Food & Dining")])
    assert m.savings_rate == 70.0
    assert m.net_savings == 7000


def test_savings_rate_negative():
    income = txn("2026-05-01", deposit=5000)
    expense = txn("2026-05-02", withdrawal=8000)
    m = compute([(income, "Salary"), (expense, "Transfer")])
    assert m.net_savings == -3000
    assert m.savings_rate == -60.0


# ── Category aggregation ─────────────────────────────────────────────────────

def test_by_category_sums():
    tagged = [
        (txn("2026-05-01", withdrawal=300), "Food & Dining"),
        (txn("2026-05-02", withdrawal=200), "Food & Dining"),
        (txn("2026-05-03", withdrawal=500), "Groceries"),
    ]
    m = compute(tagged)
    assert m.by_category["Food & Dining"] == 500
    assert m.by_category["Groceries"] == 500


def test_by_category_sorted_descending():
    tagged = [
        (txn("2026-05-01", withdrawal=100), "Groceries"),
        (txn("2026-05-02", withdrawal=900), "Transfer"),
        (txn("2026-05-03", withdrawal=400), "Food & Dining"),
    ]
    m = compute(tagged)
    amounts = list(m.by_category.values())
    assert amounts == sorted(amounts, reverse=True)


# ── Monthly breakdown ─────────────────────────────────────────────────────────

def test_monthly_grouping():
    tagged = [
        (txn("2026-05-15", deposit=10000), "Salary"),
        (txn("2026-05-20", withdrawal=2000), "Food & Dining"),
        (txn("2026-06-10", deposit=10000), "Salary"),
        (txn("2026-06-15", withdrawal=3000), "Groceries"),
    ]
    m = compute(tagged)
    assert len(m.monthly) == 2
    may, jun = m.monthly
    assert may.month == "2026-05"
    assert may.income == 10000
    assert may.expenses == 2000
    assert jun.month == "2026-06"
    assert jun.expenses == 3000


def test_monthly_sorted():
    tagged = [
        (txn("2026-07-01", deposit=5000), "Salary"),
        (txn("2026-05-01", deposit=5000), "Salary"),
        (txn("2026-06-01", deposit=5000), "Salary"),
    ]
    m = compute(tagged)
    months = [ms.month for ms in m.monthly]
    assert months == sorted(months)


# ── Period ────────────────────────────────────────────────────────────────────

def test_period_dates():
    tagged = [
        (txn("2026-05-10", deposit=1000), "Salary"),
        (txn("2026-05-01", withdrawal=200), "Food & Dining"),
        (txn("2026-05-25", withdrawal=300), "Groceries"),
    ]
    m = compute(tagged)
    assert str(m.period_start) == "2026-05-01"
    assert str(m.period_end) == "2026-05-25"


# ── Top expenses ──────────────────────────────────────────────────────────────

def test_top_expenses_ordered():
    tagged = [(txn("2026-05-0{}".format(i), withdrawal=i * 100), "Transfer") for i in range(1, 8)]
    m = compute(tagged)
    amounts = [e["amount"] for e in m.top_expenses]
    assert amounts == sorted(amounts, reverse=True)


def test_top_expenses_max_10():
    tagged = [(txn("2026-05-01", withdrawal=i * 10), "Transfer") for i in range(1, 20)]
    m = compute(tagged)
    assert len(m.top_expenses) <= 10


def test_top_expenses_excludes_deposits():
    tagged = [
        (txn("2026-05-01", deposit=50000), "Salary"),
        (txn("2026-05-02", withdrawal=100), "Food & Dining"),
    ]
    m = compute(tagged)
    assert all(e["amount"] > 0 for e in m.top_expenses)
    assert len(m.top_expenses) == 1