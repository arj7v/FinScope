# FinScope

A Python-based bank statement analyzer for HDFC NetBanking PDF exports. Upload a statement, get structured transaction data, category-wise spending breakdowns, and plain-English financial insights powered by Groq AI.

## What it does

- Parses HDFC bank statement PDFs into structured transaction objects
- Categorizes transactions automatically (Food & Dining, Groceries, EMI, Salary, etc.)
- Computes metrics — total income/expenses, savings rate, monthly breakdown, top expenses
- Generates a plain-English financial summary via Groq AI
- Exposes everything through a single REST API endpoint

## Tech Stack

- **Python 3.x**
- **pdfplumber** — PDF table extraction
- **Pydantic v2** — transaction data model and validation
- **Groq** — LLM-powered financial insights
- **FastAPI + Uvicorn** — REST API
- **pikepdf** — unlocking password-protected PDFs
- **pytest** — unit tests

## Project Structure

```
├── models.py          # Transaction Pydantic model
├── parser.py          # PDF → Transaction objects
├── rules.py           # Regex rules mapping narrations to categories
├── categorization.py  # Applies rules to transactions
├── metrics.py         # Aggregates transactions into summaries
├── reasoning.py       # Groq AI financial insights
├── api.py             # FastAPI POST /analyze endpoint
├── unlock.py          # Helper script to unlock password-protected PDFs
├── tests/
│   ├── test_categorization.py
│   └── test_metrics.py
└── sample_data/       # Gitignored — place unlocked PDFs here
```

## Setup

```bash
# Clone the repo
git clone https://github.com/arj7v/FinScope.git
cd FinScope

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install pdfplumber pydantic fastapi uvicorn python-multipart groq pikepdf python-dotenv pytest
```

Create a `.env` file in the project root:

```
GROQ_API_KEY=your_groq_api_key_here
```

## Usage

### If your PDF is password-protected

Edit `unlock.py` with your PDF path and password, then run:

```bash
python unlock.py
```

This saves an unlocked copy to `sample_data/`.

### Start the API server

```bash
uvicorn api:app --reload
```

### Analyze a statement

```bash
curl -X POST http://localhost:8000/analyze \
  -F "file=@sample_data/Acct_unlocked.pdf" | python -m json.tool
```

Or open `http://localhost:8000/docs` in your browser to use the Swagger UI.

### Response

```json
{
  "period": { "start": "2026-05-01", "end": "2026-05-27" },
  "summary": {
    "total_income": 13920.15,
    "total_expenses": 25310.27,
    "net_savings": -11390.12,
    "savings_rate_pct": -81.8
  },
  "by_category": {
    "Transfer": 18343.81,
    "Food & Dining": 5446.92,
    "Groceries": 636.25
  },
  "monthly": [...],
  "top_expenses": [...],
  "insights": "Your net balance for May shows a shortfall of ₹11,390...",
  "transaction_count": 70
}
```

## Categories

Transactions are automatically classified into:

| Category | Examples |
|---|---|
| Salary | SALARY, PAYROLL |
| Food & Dining | Swiggy, Zomato, McDonald's, Domino's |
| Groceries | BigBasket, Blinkit, Zepto, DMart |
| Entertainment | Netflix, Spotify, BookMyShow, Hotstar |
| Transportation | Uber, Ola, IRCTC, Rapido, FastTag |
| Shopping | Amazon, Flipkart, Myntra |
| Utilities & Bills | Airtel, Jio, electricity boards |
| Health | Apollo, Medplus, Netmeds |
| Insurance | LIC, HDFC Life, Star Health |
| Investment | Zerodha, Groww, SIP |
| EMI / Loan | NACH, ACH, EMI |
| ATM Withdrawal | ATM cash withdrawals |
| Bank Charges | CHRG, fees, penalties |
| Interest Charged | DCINT, OD interest |
| Transfer | UPI/NEFT/IMPS with no matched merchant |
| Other | Everything else |

## Running Tests

```bash
pytest tests/ -v
```

37 unit tests covering categorization rules and metrics computation.

## Pipeline

```
PDF → parser.py → categorization.py → metrics.py → reasoning.py → api.py → JSON
```