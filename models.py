from pydantic import BaseModel, field_validator
from datetime import date, datetime
from typing import Optional
import re


class Transaction(BaseModel):
    date: date
    narration: str
    ref_no: str
    value_date: date
    withdrawal: Optional[float] = None
    deposit: Optional[float] = None
    closing_balance: float

    @field_validator("withdrawal", "deposit", "closing_balance", mode="before")
    @classmethod
    def parse_amount(cls, v):
        if v is None or v == "" or v == "-":
            return None
        if isinstance(v, (int, float)):
            return float(v)
        # Remove commas from amounts like "34,371.91"
        return float(str(v).replace(",", "").strip())

    @field_validator("date", "value_date", mode="before")
    @classmethod
    def parse_date(cls, v):
        if isinstance(v, date):
            return v
        # Handle DD/MM/YY format
        return datetime.strptime(str(v).strip(), "%d/%m/%y")