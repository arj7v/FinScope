# CLAUDE.md

Guidance for Claude Code when working in this repository.

---

## Project: FinScope

A full-stack AI-powered bank statement analyser built in Python. Ingests HDFC NetBanking PDF statements, extracts and validates every transaction, categorizes spend, computes financial metrics, generates plain-English AI insights via Groq LLM, and serves everything through a FastAPI backend with a web UI and downloadable PDF report.

The PDF parsing, date formats, and amount formatting are HDFC-specific. Do not assume a generic statement structure.

---

## Architecture — fully built

```
PDF upload
  │
  ▼
parser.py ── pdfplumber table extraction, multi-line narration stitching,
             balance-diff amount recovery, two HDFC format support
  │
  ▼
categorization.py ── runs narration through regex rules in rules.py
                     returns a category string per transaction
  │
  ▼
metrics.py ── aggregates into Metrics: income/expenses, savings rate,
              by-category totals, monthly breakdown, top 10 expenses
  │
  ▼
reasoning.py ── builds structured prompt from Metrics, calls Groq LLM
                (openai/gpt-oss-20b), returns plain-English insights
  │
  ▼
api.py ── FastAPI: POST /analyze returns JSON, POST /report returns PDF
          GET / serves the web UI
  │
  ▼
report.py ── fpdf2 PDF report: summary cards, category bars, tables, insights
```

---

## Tech stack

- **Python 3.x**
- **Pydantic v2** — `Transaction` model with `field_validator(mode="before")` for raw-string parsing
- **pdfplumber** — PDF table extraction
- **pikepdf** — unlocking password-protected PDFs
- **Groq API** — LLM-powered financial insights (`openai/gpt-oss-20b`)
- **FastAPI + Uvicorn** — REST API and static file serving
- **fpdf2** — PDF report generation
- **python-dotenv** — `.env` loading for API keys
- **pytest** — unit tests (37 tests)

---

## Project structure

```
├── models.py            # Transaction Pydantic model — owns all parsing/coercion
├── parser.py            # PDF -> Transaction objects (both HDFC formats)
├── rules.py             # 18 compiled regex rules: narration -> category
├── categorization.py    # categorize(txn) -> str, categorize_all(txns) -> list
├── metrics.py           # compute(tagged) -> Metrics dataclass
├── reasoning.py         # generate_insights(metrics) -> str via Groq
├── report.py            # generate(metrics, insights) -> PDF bytes
├── api.py               # FastAPI app: /analyze, /report, / (UI)
├── static/
│   └── index.html       # Single-page web UI (dark theme, no framework)
├── tests/
│   ├── test_categorization.py   # 24 categorization unit tests
│   └── test_metrics.py          # 13 metrics unit tests
├── unlock.py            # Throwaway script — gitignored, never committed
├── .env                 # GROQ_API_KEY — gitignored, never committed
├── sample_data/         # Real unlocked PDFs — gitignored, never committed
├── Procfile             # For Railway/Render deployment
└── requirements.txt     # Production dependencies
```

---

## HDFC statement formats

### Old format (DD/MM/YY)

```
Date | Narration | Chq./Ref.No. | Value Dt | Withdrawal Amt. | Deposit Amt. | Closing Balance
```

- Date: `DD/MM/YY` — parse with `datetime.strptime(v, "%d/%m/%y")`
- Multiple transactions can be stacked in a single table row (multi-txn rows)
- Empty cells for absent withdrawal/deposit — blank or `-`
- Amount direction derived from **closing balance deltas**, not column position
  (pdfplumber silently drops blank cells, making column position unreliable)
- Multi-line narrations stitched using `NEW_TXN_RE` prefix matching

### New format (DD/MM/YYYY)

```
Date | Narration | Chq. / Ref No. | Value Date | Withdrawal Amount | Deposit Amount | Closing Balance*
```

- Date: `DD/MM/YYYY` — parse with `datetime.strptime(v, "%d/%m/%Y")`
- One transaction per row — simpler, no balance-diff needed
- `0.00` for absent withdrawal/deposit (not blank)
- Multi-line narration is within a single cell (newlines stripped to spaces)

Format is auto-detected by date string length: 8 chars = old, 10 chars = new.

---

## Categorization rules (rules.py)

18 compiled regex patterns, checked in order, first match wins:

| Category | Key patterns |
|---|---|
| Salary | SALARY, PAYROLL, STIPEND |
| Interest Earned | INTEREST CREDIT, SAVINGS INT |
| EMI / Loan | NACH, ACH, EMI |
| Food & Dining | SWIGGY, ZOMATO, MCDONALDS, DOMINOS, PIZZA, RESTAURANT |
| Groceries | BIGBASKET, BLINKIT, ZEPTO, DMART, JIOMART |
| Entertainment | NETFLIX, SPOTIFY, HOTSTAR, BOOKMYSHOW, PVR |
| Transportation | UBER, OLA, IRCTC, RAPIDO, FASTAG, INDIGO |
| Shopping | AMAZON, FLIPKART, MYNTRA, MEESHO, NYKAA |
| Utilities & Bills | AIRTEL, JIO, VODAFONE, BESCOM, ELECTRICITY |
| Health | APOLLO, MEDPLUS, NETMEDS, HOSPITAL, PHARMA |
| Insurance | LIC, INSURANCE, HDFC LIFE, STAR HEALTH |
| Investment | MUTUAL FUND, SIP, ZERODHA, GROWW, KUVERA |
| ATM Withdrawal | ATM- prefix |
| Bank Charges | CHRG prefix, CHARGES, PENALTY |
| Interest Charged | INT. prefix, DCINT prefix, OD INT |
| Transfer | UPI/NEFT/IMPS/RTGS catch-all (no merchant match) |
| Other | Everything else |

To add a new merchant: edit `rules.py` only. Do not touch `categorization.py`.

---

## Conventions

- **Parser extracts and groups. Model validates and coerces.** All raw-string cleaning (comma stripping, date parsing) lives in `field_validator(mode="before")` in `models.py`. Do not put type conversion in `parser.py`.
- **rules.py is the only file to edit for new categories/merchants.** Keep parsing and categorization logic strictly separated.
- **Dates:** always use `datetime.strptime(...).date()` — `date` has no `strptime`. This was a real prior bug; do not reintroduce it.
- **Amounts:** strip commas before float conversion — Indian grouping (`1,23,456.78`).
- **PDF report text:** all strings must pass through `_s()` in `report.py` before being written — fpdf2's Helvetica font is latin-1 only; Groq responses contain em dashes, curly quotes, and `₹` which must be mapped to ASCII equivalents.
- `unlock.py` is intentionally gitignored — it holds real PDF passwords. Never commit it.
- `sample_data/` is gitignored — contains real bank statement data. Never commit it.
- `.env` is gitignored — holds `GROQ_API_KEY`. Never commit it.

---

## Running locally

```bash
# Install dependencies
pip install -r requirements.txt

# Set API key
echo "GROQ_API_KEY=your_key_here" > .env

# Start server
uvicorn api:app --reload

# Open browser
open http://localhost:8000

# Run tests
pytest tests/ -v
```

## Unlocking a password-protected PDF

Edit `unlock.py` with your file path and password, then:
```bash
python unlock.py
```

---

## Current state — accurate

**Fully built and working:**
- PDF parsing — both HDFC formats, 70+ transactions from real statements
- Categorization — 18 rules, 37 passing unit tests
- Metrics — income/expenses/savings rate, monthly breakdown, top expenses
- Groq LLM reasoning — plain-English insights with actionable suggestions
- FastAPI REST API — `POST /analyze` (JSON), `POST /report` (PDF download)
- Web UI — dark theme, file upload, summary cards, category bars, insights display
- PDF report — fpdf2, formatted with colours, bars, tables, and AI insights
- Deployment-ready — `Procfile` + `requirements.txt` for Railway/Render

**Not built (deliberate scope decisions):**
- SQLite persistence — transactions are in-memory per request
- Docker / CI pipeline
- Source traceability in LLM responses (citing individual transaction IDs)
- Risk predicates / rule engine

---

## Deployment

Hosted on Railway/Render via GitHub integration.

```
Procfile:  web: uvicorn api:app --host 0.0.0.0 --port $PORT
Env vars:  GROQ_API_KEY (set in platform dashboard — never in code)
```