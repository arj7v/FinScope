import tempfile
import os
from dataclasses import asdict

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse, Response
from fastapi.staticfiles import StaticFiles

from parser import parse_statement
from categorization import categorize_all
from metrics import compute
from reasoning import generate_insights
from report import generate as generate_pdf

app = FastAPI(title="FinScope", version="0.1.0")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def index():
    with open("static/index.html") as f:
        return f.read()


def _run_pipeline(pdf_bytes: bytes):
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(pdf_bytes)
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
    return m, insights, len(transactions)


@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    m, insights, count = _run_pipeline(await file.read())

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
        "transaction_count": count,
    })


@app.post("/report")
async def report(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    m, insights, _ = _run_pipeline(await file.read())
    pdf_bytes = generate_pdf(m, insights)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=finscope_report.pdf"},
    )