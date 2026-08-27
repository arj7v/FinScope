import re
from typing import List

import pdfplumber

from models import Transaction


HEADER_ROW = {"date", "narration", "chq./ref.no.", "valuedt", "withdrawalamt.", "depositamt.", "closingbalance"}
DATE_RE = re.compile(r"^\d{2}/\d{2}/\d{2}$")
ALNUM_RE = re.compile(r"[^A-Z0-9]")
# Line begins a new transaction if it starts with one of these markers.
# UPI- requires a letter after the dash, since `UPI-648862497443-UPI` is a continuation.
NEW_TXN_RE = re.compile(
    r"^("
    r"UPI[-\s][A-Z]"
    r"|NEFT[-\s]"
    r"|IMPS[-\s]"
    r"|RTGS[-\s]"
    r"|NACH[-\s]"
    r"|ACH[-\s]"
    r"|EMI[-\s]"
    r"|ATM[-\s]"
    r"|POS"
    r"|CHRG"
    r"|INT\."
    r"|CASH"
    r"|MED"
    r"|DCINT"
    r"|TPT[-\s]"
    r"|BRN[-\s]"
    r"|IB[-\s]"
    r"|INB[-\s]"
    r"|BIL[-\s]"
    r"|EPI"
    r")",
    re.IGNORECASE,
)


def _is_header(row: list) -> bool:
    values = {str(v).replace(" ", "").lower() for v in row if v}
    return bool(values & HEADER_ROW)


def _split_cell(cell) -> list:
    if not cell:
        return []
    return [v.strip() for v in str(cell).split("\n") if v.strip()]


def _parse_amount(v):
    if v in (None, "", "-"):
        return None
    return float(str(v).replace(",", "").strip())


def _group_narrations(narration_lines: list, n: int) -> list:
    """Group wrapped narration lines into one entry per transaction. A line is treated as a new
    transaction start if it matches NEW_TXN_RE; everything else is a continuation of the
    previous line. If the resulting count doesn't match n, pad or merge to fit."""
    if not narration_lines:
        return [""] * n

    groups = []
    current = []
    for line in narration_lines:
        if NEW_TXN_RE.match(line) and current:
            groups.append(" ".join(current))
            current = [line]
        else:
            current.append(line)
    if current:
        groups.append(" ".join(current))

    if len(groups) == n:
        return groups
    if len(groups) < n:
        return groups + [""] * (n - len(groups))
    return groups[: n - 1] + [" ".join(groups[n - 1:])]


def parse_statement(pdf_path: str) -> List[Transaction]:
    transactions = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            table = page.extract_table()
            if not table:
                continue

            for row in table:
                if not row or not row[0] or _is_header(row):
                    continue

                dates = _split_cell(row[0])
                if not dates or not DATE_RE.match(dates[0]):
                    continue

                narration_lines = _split_cell(row[1])
                ref_nos = _split_cell(row[2])
                value_dates = _split_cell(row[3])
                withdrawal_amts = [_parse_amount(v) for v in _split_cell(row[4])]
                deposit_amts = [_parse_amount(v) for v in _split_cell(row[5])]
                balances = [_parse_amount(v) for v in _split_cell(row[6])]

                n = len(dates)
                if len(balances) != n:
                    print(f"Skipping row: {n} dates but {len(balances)} balances")
                    continue

                w_sum = sum(a for a in withdrawal_amts if a is not None)
                d_sum = sum(a for a in deposit_amts if a is not None)
                opening = round(balances[-1] + w_sum - d_sum, 2)

                narrations = _group_narrations(narration_lines, n)

                prev_balance = opening
                for i in range(n):
                    cur_balance = balances[i]
                    diff = round(cur_balance - prev_balance, 2)
                    if diff < 0:
                        withdrawal, deposit = -diff, None
                    elif diff > 0:
                        withdrawal, deposit = None, diff
                    else:
                        withdrawal, deposit = None, None
                    prev_balance = cur_balance

                    try:
                        txn = Transaction(
                            date=dates[i],
                            narration=narrations[i] if i < len(narrations) else "",
                            ref_no=ref_nos[i] if i < len(ref_nos) else "",
                            value_date=value_dates[i] if i < len(value_dates) else dates[i],
                            withdrawal=withdrawal,
                            deposit=deposit,
                            closing_balance=cur_balance,
                        )
                        transactions.append(txn)
                    except Exception as e:
                        print(f"Skipping txn {i}: {e}")
                        continue

    return transactions


if __name__ == "__main__":
    txns = parse_statement("sample_data/Acct_unlocked.pdf")
    print(f"Parsed {len(txns)} transactions\n")
    for t in txns:
        kind = f"W {t.withdrawal:>10.2f}" if t.withdrawal else f"D {t.deposit:>10.2f}"
        print(f"{t.date}  {kind}  bal={t.closing_balance:>10.2f}  {t.narration[:60]}")
