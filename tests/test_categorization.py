import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import date
from models import Transaction
from categorization import categorize

# Shared dummy values for non-narration fields
_D = date(2026, 5, 1)
_BASE = dict(date=_D, ref_no="REF", value_date=_D, closing_balance=10000.0)


def txn(narration: str, withdrawal=None, deposit=None) -> Transaction:
    return Transaction(narration=narration, withdrawal=withdrawal, deposit=deposit, **_BASE)


# ── Food & Dining ─────────────────────────────────────────────────────────────

def test_swiggy():
    assert categorize(txn("UPI-SWIGGY-UPISWIGGY@ICICI", withdrawal=300)) == "Food & Dining"

def test_zomato():
    assert categorize(txn("UPI-ZOMATO-ZOMATOPAY@HDFC", withdrawal=250)) == "Food & Dining"

def test_mcdonalds():
    assert categorize(txn("UPI-MCDONALDS HARDCASTLE-MCDONALDSINNOVITI@YBL", withdrawal=149)) == "Food & Dining"

def test_dominos():
    assert categorize(txn("UPI-DOMINOS PIZZA-DOMINOS@ICICI", withdrawal=499)) == "Food & Dining"


# ── Groceries ────────────────────────────────────────────────────────────────

def test_zepto():
    assert categorize(txn("UPI-ZEPTOMARKETPLACE PR-ZEPTO.PAYU@AXIS", withdrawal=250)) == "Groceries"

def test_bigbasket():
    assert categorize(txn("UPI-BIGBASKET-BB@HDFCBANK", withdrawal=800)) == "Groceries"

def test_blinkit():
    assert categorize(txn("UPI-BLINKIT-BLINKIT@PAYTM", withdrawal=350)) == "Groceries"


# ── Entertainment ─────────────────────────────────────────────────────────────

def test_netflix():
    assert categorize(txn("UPI-NETFLIX-NETFLIX@HDFC", withdrawal=649)) == "Entertainment"

def test_spotify():
    assert categorize(txn("UPI-SPOTIFY-SPOTIFY@ICICI", withdrawal=119)) == "Entertainment"

def test_bookmyshow():
    assert categorize(txn("UPI-BOOKMYSHOW-BMS@YESBANK", withdrawal=500)) == "Entertainment"


# ── Transportation ────────────────────────────────────────────────────────────

def test_uber():
    assert categorize(txn("UPI-UBER INDIA-UBER@HDFC", withdrawal=200)) == "Transportation"

def test_irctc():
    assert categorize(txn("NEFT- IRCTC TICKET BOOKING", withdrawal=1200)) == "Transportation"


# ── EMI / Loan ────────────────────────────────────────────────────────────────

def test_nach():
    assert categorize(txn("NACH- HDFC BANK HOME LOAN EMI", withdrawal=15000)) == "EMI / Loan"

def test_emi():
    assert categorize(txn("EMI- BAJAJ FINANCE", withdrawal=3000)) == "EMI / Loan"


# ── Salary ────────────────────────────────────────────────────────────────────

def test_salary_credit():
    assert categorize(txn("SALARY CREDIT ACME CORP", deposit=80000)) == "Salary"

def test_neft_salary():
    assert categorize(txn("NEFT- SAL JUN 2026 ACME", deposit=80000)) == "Salary"


# ── Bank Charges & Interest ───────────────────────────────────────────────────

def test_bank_charges():
    assert categorize(txn("CHRG SMS ALERT CHARGES", withdrawal=10)) == "Bank Charges"

def test_interest_charged():
    assert categorize(txn("DCINTLPOSTXNDCC+ST210426-EPR123", withdrawal=4)) == "Interest Charged"

def test_interest_earned():
    assert categorize(txn("INTEREST CREDIT SAVINGS", deposit=120)) == "Interest Earned"


# ── ATM ───────────────────────────────────────────────────────────────────────

def test_atm_withdrawal():
    assert categorize(txn("ATM- WDL 123456 KORAMANGALA", withdrawal=5000)) == "ATM Withdrawal"


# ── Transfer catch-all ────────────────────────────────────────────────────────

def test_upi_unknown_merchant():
    assert categorize(txn("UPI-JOHN DOE-JOHNDOE@OKSBI", withdrawal=500)) == "Transfer"

def test_neft_transfer():
    assert categorize(txn("NEFT- RENT PAYMENT", withdrawal=20000)) == "Transfer"

def test_imps():
    assert categorize(txn("IMPS- 123456789 FRIEND", withdrawal=1000)) == "Transfer"


# ── Other (no match) ─────────────────────────────────────────────────────────

def test_unknown_narration():
    assert categorize(txn("MEDCSI223487XXXXXX0400GOOGLEWORKSP", withdrawal=829)) == "Other"