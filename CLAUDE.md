# CLAUDE.md

Guidance for Claude Code when working in this repository.

## Project: Finscope

A Python bank statement parser. It ingests HDFC NetBanking PDF statements and extracts transactions into structured, validated data objects. The PDF layout, date format, and amount formatting are HDFC-specific — do not assume generic statement structure.

Pipeline (target end state):

```
PDF export  ->  unlock (if password-protected)  ->  extract raw rows
            ->  map rows to Transaction objects  ->  structured output
```

## Tech stack

- Python 3.x
- Pydantic (v2) for the data model — uses `field_validator` with `mode="before"`
- `pikepdf` for unlocking password-protected PDFs
- PDF text/table extraction library for `parser.py` (to be decided when building it)

## Project structure

```
app/
  models.py      # Transaction Pydantic model (DONE)
  parser.py      # PDF -> raw rows -> Transaction objects (NEXT)
sample_data/     # unlocked PDFs live here — gitignored, never commit
unlock.py        # throwaway helper for password-protected PDFs (pikepdf)
```

## HDFC statement format (domain knowledge — read before touching parsing)

Column layout in the source PDF, left to right:

```
Date | Narration | Chq./Ref.No. | Value Dt | Withdrawal Amt. | Deposit Amt. | Closing Balance
```

Format quirks that the parser and validators must handle:

- **Dates** are `DD/MM/YY`. Parse with `datetime.strptime(value, "%d/%m/%y").date()`.
  Note: it is `datetime.strptime(...).date()`, NOT `date.strptime(...)` — `date` has no `strptime`. This was a real bug; don't reintroduce it.
- **Amounts** (`Withdrawal Amt.`, `Deposit Amt.`, `Closing Balance`) are comma-formatted strings, e.g. `1,23,456.78` (Indian grouping). Strip commas before converting to a numeric type.
- **Narration** is messy and frequently **multi-line** — UPI IDs, reference numbers, and merchant strings spill across rows. The raw text extraction will produce continuation lines that belong to the preceding transaction. The parser must stitch these back together rather than treating each text line as a new row.
- A given transaction has a value in **either** `Withdrawal Amt.` **or** `Deposit Amt.`, not both. Treat empty cells accordingly.

## Conventions

- Validators on the `Transaction` model use `field_validator` with `mode="before"` so they receive the raw string straight from the PDF and own all parsing/cleaning. Keep parsing logic in the validators, not scattered through `parser.py`.
- `parser.py`'s job is to extract and correctly group raw rows; the model's job is to validate and coerce. Keep that boundary clean.
- Never commit anything under `sample_data/` — it contains real (unlocked) statement data. Confirm it's in `.gitignore` before any commit.
- `unlock.py` is intentionally a throwaway script, kept out of the main `app/` package.

## Current state

- Project setup: done
- `Transaction` model in `app/models.py`: done
- `app/parser.py`: **not started — this is the next piece of work**

## When extending this project

- New parsing edge cases discovered in real statements should be reflected here so they aren't rediscovered.
- If a second bank format is ever added, refactor toward a per-bank parser/model strategy rather than branching inside the HDFC path.
