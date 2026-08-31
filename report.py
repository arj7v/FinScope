from fpdf import FPDF
from metrics import Metrics


_ACCENT = (99, 102, 241)   # indigo
_DARK   = (30, 30, 46)
_GRAY   = (100, 100, 120)
_LIGHT  = (245, 245, 250)
_GREEN  = (34, 197, 94)
_RED    = (239, 68, 68)


class _PDF(FPDF):
    def header(self):
        self.set_fill_color(*_DARK)
        self.rect(0, 0, 210, 18, "F")
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(255, 255, 255)
        self.set_xy(0, 4)
        self.cell(210, 10, "FinScope — Financial Report", align="C")
        self.set_text_color(0, 0, 0)
        self.ln(12)

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(*_GRAY)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")


def _section(pdf: _PDF, title: str):
    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(*_ACCENT)
    pdf.cell(0, 8, title, ln=True)
    pdf.set_draw_color(*_ACCENT)
    pdf.set_line_width(0.4)
    pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + 190, pdf.get_y())
    pdf.ln(2)
    pdf.set_text_color(0, 0, 0)


def _kv(pdf: _PDF, label: str, value: str, color=None):
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(*_GRAY)
    pdf.cell(70, 7, label)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(*(color or _DARK))
    pdf.cell(0, 7, value, ln=True)
    pdf.set_text_color(0, 0, 0)


def _bar(pdf: _PDF, label: str, amount: float, max_amount: float):
    bar_width = 90
    filled = int((amount / max_amount) * bar_width) if max_amount else 0
    y = pdf.get_y()
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(*_DARK)
    pdf.cell(55, 6, label[:30])
    pdf.set_fill_color(*_ACCENT)
    pdf.rect(pdf.get_x(), y + 1, filled, 4, "F")
    pdf.set_fill_color(*_LIGHT)
    pdf.rect(pdf.get_x() + filled, y + 1, bar_width - filled, 4, "F")
    pdf.set_xy(pdf.get_x() + bar_width + 3, y)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(30, 6, f"Rs {amount:,.0f}", ln=True)


def generate(m: Metrics, insights: str) -> bytes:
    pdf = _PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_margins(10, 20, 10)

    # ── Period ────────────────────────────────────────────────────────────────
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(*_GRAY)
    pdf.cell(0, 6, f"Statement period: {m.period_start}  to  {m.period_end}", ln=True)
    pdf.ln(2)

    # ── Overview cards ────────────────────────────────────────────────────────
    _section(pdf, "Overview")
    _kv(pdf, "Total Income",    f"Rs {m.total_income:,.2f}",   _GREEN)
    _kv(pdf, "Total Expenses",  f"Rs {m.total_expenses:,.2f}", _RED)
    savings_color = _GREEN if m.net_savings >= 0 else _RED
    _kv(pdf, "Net Savings",     f"Rs {m.net_savings:,.2f}",    savings_color)
    _kv(pdf, "Savings Rate",    f"{m.savings_rate}%",          savings_color)

    # ── Spending by category ──────────────────────────────────────────────────
    _section(pdf, "Spending by Category")
    max_amt = max(m.by_category.values(), default=1)
    for cat, amt in m.by_category.items():
        _bar(pdf, cat, amt, max_amt)

    # ── Monthly breakdown ─────────────────────────────────────────────────────
    _section(pdf, "Monthly Breakdown")
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(*_LIGHT)
    pdf.set_text_color(*_DARK)
    pdf.cell(35, 7, "Month",    fill=True)
    pdf.cell(45, 7, "Income",   fill=True)
    pdf.cell(45, 7, "Expenses", fill=True)
    pdf.cell(45, 7, "Net",      fill=True, ln=True)
    pdf.set_font("Helvetica", "", 9)
    for ms in m.monthly:
        net_c = _GREEN if ms.net >= 0 else _RED
        pdf.set_text_color(*_DARK)
        pdf.cell(35, 6, ms.month)
        pdf.cell(45, 6, f"Rs {ms.income:,.0f}")
        pdf.cell(45, 6, f"Rs {ms.expenses:,.0f}")
        pdf.set_text_color(*net_c)
        pdf.cell(45, 6, f"Rs {ms.net:,.0f}", ln=True)
        pdf.set_text_color(0, 0, 0)

    # ── Top expenses ──────────────────────────────────────────────────────────
    _section(pdf, "Top Expenses")
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(*_LIGHT)
    pdf.set_text_color(*_DARK)
    pdf.cell(25, 7, "Date",     fill=True)
    pdf.cell(30, 7, "Amount",   fill=True)
    pdf.cell(35, 7, "Category", fill=True)
    pdf.cell(100, 7, "Narration", fill=True, ln=True)
    pdf.set_font("Helvetica", "", 8)
    for e in m.top_expenses:
        pdf.set_text_color(*_DARK)
        pdf.cell(25, 5, str(e["date"]))
        pdf.set_text_color(*_RED)
        pdf.cell(30, 5, f"Rs {e['amount']:,.0f}")
        pdf.set_text_color(*_GRAY)
        pdf.cell(35, 5, e["category"][:18])
        pdf.cell(100, 5, e["narration"][:55], ln=True)
        pdf.set_text_color(0, 0, 0)

    # ── AI Insights ───────────────────────────────────────────────────────────
    _section(pdf, "AI Financial Insights")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(*_DARK)
    pdf.set_fill_color(*_LIGHT)
    pdf.rect(10, pdf.get_y(), 190, 4, "F")
    pdf.ln(5)
    pdf.multi_cell(190, 6, insights.strip())

    return bytes(pdf.output())