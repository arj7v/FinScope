from dotenv import load_dotenv
from groq import Groq

from metrics import Metrics

load_dotenv()

_CLIENT: Groq | None = None
_MODEL = "openai/gpt-oss-20b"


def _client() -> Groq:
    global _CLIENT
    if _CLIENT is None:
        _CLIENT = Groq()
    return _CLIENT


def _build_prompt(m: Metrics) -> str:
    monthly_lines = "\n".join(
        f"  {ms.month}: income ₹{ms.income:,.0f}, expenses ₹{ms.expenses:,.0f}, "
        f"net ₹{ms.net:,.0f}"
        for ms in m.monthly
    )
    category_lines = "\n".join(
        f"  {cat}: ₹{amt:,.0f}" for cat, amt in m.by_category.items()
    )
    top_lines = "\n".join(
        f"  {e['date']}  ₹{e['amount']:,.0f}  [{e['category']}]  {e['narration'][:70]}"
        for e in m.top_expenses
    )

    return f"""You are a friendly, concise personal finance advisor.

Below is a summary of a user's bank statement from {m.period_start} to {m.period_end}.
All amounts are in Indian Rupees (₹).

OVERVIEW
  Total income  : ₹{m.total_income:,.2f}
  Total expenses: ₹{m.total_expenses:,.2f}
  Net savings   : ₹{m.net_savings:,.2f}
  Savings rate  : {m.savings_rate}%

SPENDING BY CATEGORY
{category_lines}

MONTHLY BREAKDOWN
{monthly_lines}

TOP 10 EXPENSES
{top_lines}

Write a clear, plain-English financial summary for the user. Cover:
1. Overall financial health (income vs expenses, savings rate).
2. Biggest spending categories and whether any look unusually high.
3. Month-over-month trends (if the period spans multiple months).
4. 2–3 actionable suggestions to improve savings or reduce unnecessary spend.

Keep the response under 300 words. Use ₹ for all amounts. No markdown headers — \
use short paragraphs instead."""


def generate_insights(m: Metrics) -> str:
    response = _client().chat.completions.create(
        model=_MODEL,
        max_tokens=1024,
        messages=[
            {"role": "system", "content": "You are a friendly, concise personal finance advisor."},
            {"role": "user", "content": _build_prompt(m)},
        ],
    )
    return response.choices[0].message.content