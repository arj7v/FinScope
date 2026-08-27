from models import Transaction
from rules import RULES, CATEGORY_UNKNOWN


def categorize(txn: Transaction) -> str:
    narration = txn.narration.strip()
    for pattern, category in RULES:
        if pattern.search(narration):
            return category
    return CATEGORY_UNKNOWN


def categorize_all(transactions: list[Transaction]) -> list[tuple[Transaction, str]]:
    return [(txn, categorize(txn)) for txn in transactions]