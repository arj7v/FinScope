import tempfile
import os
from dataclasses import asdict

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse

from parser import parse_statement
from categorization import categorize_all
from metrics import compute
from reasoning import generate_insights

app = FastAPI(title="FinScope", version="0.1.0")


@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        transactions = parse_statement(tmp_path)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Failed to parse PDF: {e}")
    finally:
        os.unlink(tmp_path)

    if not transactions:
        raise HTTPException(status_code=422, detail="No transactions found in statement.")

    tagged = categorize_all(transactions)
    m = compute(tagged)
    insights = generate_insights(m)

    return JSONResponse({
        "period": {"start": str(m.period_start), "end": str(m.period_end)},
        "summary": {
            "total_income": m.total_income,
            "total_expenses": m.total_expenses,
            "net_savings": m.net_savings,
            "savings_rate_pct": m.savings_rate,
        },
        "by_category": m.by_category,
        "monthly": [asdict(ms) for ms in m.monthly],
        "top_expenses": m.top_expenses,
        "insights": insights,
        "transaction_count": len(transactions),
    })