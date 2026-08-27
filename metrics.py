from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date

from models import Transaction


@dataclass
class MonthSummary:
    month: str                          # "YYYY-MM"
    income: float = 0.0
    expenses: float = 0.0
    by_category: dict[str, float] = field(default_factory=dict)

    @property
    def net(self) -> float:
        return round(self.income - self.expenses, 2)


@dataclass
class Metrics:
    period_start: date
    period_end: date
    total_income: float
    total_expenses: float
    net_savings: float
    savings_rate: float                 # 0–100 (%)
    by_category: dict[str, float]       # category -> total withdrawal amount
    monthly: list[MonthSummary]
    top_expenses: list[dict]            # top 10 individual withdrawal transactions


def compute(tagged: list[tuple[Transaction, str]]) -> Metrics:
    if not tagged:
        today = date.today()
        return Metrics(today, today, 0, 0, 0, 0.0, {}, [], [])

    dates = [t.date for t, _ in tagged]
    period_start, period_end = min(dates), max(dates)

    total_income = sum(t.deposit or 0.0 for t, _ in tagged)
    total_expenses = sum(t.withdrawal or 0.0 for t, _ in tagged)
    net_savings = round(total_income - total_expenses, 2)
    savings_rate = round((net_savings / total_income * 100) if total_income else 0.0, 1)

    by_category: dict[str, float] = defaultdict(float)
    monthly_map: dict[str, MonthSummary] = {}

    for txn, cat in tagged:
        month_key = txn.date.strftime("%Y-%m")
        if month_key not in monthly_map:
            monthly_map[month_key] = MonthSummary(month=month_key)
        ms = monthly_map[month_key]

        if txn.deposit:
            ms.income = round(ms.income + txn.deposit, 2)
        if txn.withdrawal:
            ms.expenses = round(ms.expenses + txn.withdrawal, 2)
            by_category[cat] = round(by_category[cat] + txn.withdrawal, 2)
            ms.by_category[cat] = round(ms.by_category.get(cat, 0.0) + txn.withdrawal, 2)

    monthly = [monthly_map[k] for k in sorted(monthly_map)]

    top_withdrawals = sorted(
        [(t, cat) for t, cat in tagged if t.withdrawal],
        key=lambda x: x[0].withdrawal,  # type: ignore[arg-type]
        reverse=True,
    )[:10]
    top_expenses = [
        {
            "date": str(t.date),
            "narration": t.narration,
            "category": cat,
            "amount": t.withdrawal,
        }
        for t, cat in top_withdrawals
    ]

    return Metrics(
        period_start=period_start,
        period_end=period_end,
        total_income=round(total_income, 2),
        total_expenses=round(total_expenses, 2),
        net_savings=net_savings,
        savings_rate=savings_rate,
        by_category=dict(sorted(by_category.items(), key=lambda x: x[1], reverse=True)),
        monthly=monthly,
        top_expenses=top_expenses,
    )