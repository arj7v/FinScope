import re
from typing import List, Tuple

# Each rule is (compiled_pattern, category). First match wins.
# Patterns are matched case-insensitively against the full narration string.

_RAW: List[Tuple[str, str]] = [
    # ── Income ──────────────────────────────────────────────────────────────
    (r"SALARY|SAL(?:ARY)?[-\s]|PAYROLL|STIPEND", "Salary"),
    (r"INTEREST\s+CREDIT|INT\s+CREDIT|SAVINGS\s+INT", "Interest Earned"),
    (r"DIVIDEND|DIV\s+CREDIT", "Dividend"),
    (r"REFUND|CASHBACK|REVERSAL", "Refund / Cashback"),

    # ── EMI / Loans ──────────────────────────────────────────────────────────
    (r"NACH[-\s]|ACH[-\s]|EMI[-\s]|LOAN\s+EMI|EQUATED", "EMI / Loan"),

    # ── Food & Dining ─────────────────────────────────────────────────────────
    (r"SWIGGY|ZOMATO|EAZYDINER|DINEOUT|DOMINOS|DOMINOES|PIZZA|BURGER"
     r"|MCDONALDS|KFC|SUBWAY|STARBUCKS|CAFE|RESTAURANT|DINING|FOOD",
     "Food & Dining"),

    # ── Groceries ─────────────────────────────────────────────────────────────
    (r"BIGBASKET|BIG\s*BASKET|BLINKIT|ZEPTO|DMART|D[-\s]MART"
     r"|JIOMART|JIO\s*MART|GROFERS|INSTAMART|SUPERMART|GROCERY|KIRANA",
     "Groceries"),

    # ── Entertainment ─────────────────────────────────────────────────────────
    (r"NETFLIX|SPOTIFY|HOTSTAR|DISNEYPLUS|DISNEY[-\s]PLUS|AMAZON\s*PRIME"
     r"|YOUTUBE|BOOKMYSHOW|PVR|INOX|PVRINOX|MXPLAYER|JIOCINEMA|HUNGAMA"
     r"|SONYLIV|ZEESEE|ZEE5|APPLE\s*TV|GAMEPASS|STEAM",
     "Entertainment"),

    # ── Transportation ────────────────────────────────────────────────────────
    (r"UBER|OLA\s*CAB|RAPIDO|METRO|BMTC|KSRTC|IRCTC|RAILWAY|INDIGO"
     r"|SPICEJET|AIRINDIA|VISTARA|MAKEMYTRIP|GOIBIBO|CLEARTRIP|REDBUS"
     r"|YATRA|FASTAG|NHAI|TOLL",
     "Transportation"),

    # ── Shopping ──────────────────────────────────────────────────────────────
    (r"AMAZON(?!\s*PRIME)|FLIPKART|MYNTRA|MEESHO|AJIO|NYKAA|TATACLIQ"
     r"|SNAPDEAL|SHOPIFY|FIRSTCRY|RELIANCE\s*DIGITAL|CROMA|VIJAY\s*SALES",
     "Shopping"),

    # ── Utilities & Bills ─────────────────────────────────────────────────────
    (r"ELECTRICITY|BESCOM|MSEDCL|TATA\s*POWER|BSES|RELIANCE\s*ENERGY"
     r"|AIRTEL|JIO(?:FIBER)?|VODAFONE|BSNL|TATA\s*SKY|TATASKY|DISH\s*TV"
     r"|D2H|MAHANAGAR\s*GAS|INDANE|HP\s*GAS|BHARAT\s*GAS|PIPED\s*GAS"
     r"|WATER\s*BILL|MUNICIPALITY|BROADBAND|INTERNET\s*BILL|POSTPAID"
     r"|RECHARGE",
     "Utilities & Bills"),

    # ── Health ────────────────────────────────────────────────────────────────
    (r"APOLLO|MEDPLUS|NETMEDS|1MG|PHARMEASY|TATA\s*1MG|PHARMA(?:CY)?"
     r"|HOSPITAL|CLINIC|DIAGNOSTIC|HEALTHKART|DOCPRIME|PRACTO|LYBRATE"
     r"|DENTIST|DOCTOR|MEDICAL|HEALTH",
     "Health"),

    # ── Insurance ────────────────────────────────────────────────────────────
    (r"LIC\b|LIFE\s*INSUR|INSURANCE|INSUR(?:ANCE)?|HDFC\s*LIFE|ICICI\s*PRU"
     r"|BAJAJ\s*ALLIANZ|MAX\s*LIFE|TATA\s*AIA|STAR\s*HEALTH|NIVA\s*BUPA"
     r"|RELIGARE",
     "Insurance"),

    # ── Investment ────────────────────────────────────────────────────────────
    (r"MUTUAL\s*FUND|SIP[-\s]|ZERODHA|GROWW|KUVERA|COIN\b|PAYTM\s*MONEY"
     r"|SMALLCASE|ETMONEY|SCRIPBOX|WEALTHDESK|NSDL|CDSL|DEMAT|NSE|BSE"
     r"|EQUITY|STOCK",
     "Investment"),

    # ── ATM ───────────────────────────────────────────────────────────────────
    (r"^ATM[-\s]|ATM\s*WITHDRAWAL|CASH\s*WITHDRAWAL", "ATM Withdrawal"),

    # ── Bank Charges ──────────────────────────────────────────────────────────
    (r"^CHRG|CHARGES?|PENALTY|FINE\b|SMS\s*CHARGE|ANNUAL\s*FEE|CARD\s*FEE"
     r"|PROCESSING\s*FEE|GST\b",
     "Bank Charges"),

    # ── Interest Charged ─────────────────────────────────────────────────────
    (r"^INT\.|^DCINT|INTEREST\s*CHARGED|INTEREST\s*DEBIT|FINANCE\s*CHARGE|OD\s*INT",
     "Interest Charged"),

    # ── Transfer (catch-all for UPI/NEFT/IMPS/RTGS with no merchant match) ───
    (r"^UPI[-\s]|^NEFT[-\s]|^IMPS[-\s]|^RTGS[-\s]|^IB[-\s]|^INB[-\s]"
     r"|^BIL[-\s]|^TPT[-\s]|^BRN[-\s]|^EPI",
     "Transfer"),
]

RULES: List[Tuple[re.Pattern, str]] = [
    (re.compile(pattern, re.IGNORECASE), category)
    for pattern, category in _RAW
]

CATEGORY_UNKNOWN = "Other"