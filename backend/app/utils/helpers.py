"""
General utility functions
"""

import re
from typing import Optional
from datetime import datetime, date


def slugify(text: str) -> str:
    """
    Convert text to URL-friendly slug.

    Args:
        text: Text to slugify

    Returns:
        Slugified text
    """
    # Convert to lowercase
    text = text.lower()

    # Replace spaces and underscores with hyphens
    text = re.sub(r"[\s_]+", "-", text)

    # Remove non-alphanumeric characters (except hyphens)
    text = re.sub(r"[^a-z0-9-]", "", text)

    # Remove multiple consecutive hyphens
    text = re.sub(r"-+", "-", text)

    # Remove leading/trailing hyphens
    text = text.strip("-")

    return text


def generate_receipt_number(prefix: str = "R") -> str:
    """
    Generate a unique receipt number.

    Args:
        prefix: Prefix for the receipt number

    Returns:
        Receipt number (e.g., R-20250106-123456)
    """
    now = datetime.utcnow()
    date_part = now.strftime("%Y%m%d")
    time_part = now.strftime("%H%M%S")

    return f"{prefix}-{date_part}-{time_part}"


def format_currency(amount: float, currency: str = "EUR") -> str:
    """
    Format amount as currency string.

    Args:
        amount: Amount to format
        currency: Currency code

    Returns:
        Formatted currency string
    """
    if currency == "EUR":
        return f"{amount:.2f} €"
    elif currency == "USD":
        return f"${amount:.2f}"
    else:
        return f"{amount:.2f} {currency}"


def parse_date(date_str: Optional[str]) -> Optional[date]:
    """
    Parse date string in various formats.

    Args:
        date_str: Date string to parse

    Returns:
        Parsed date or None
    """
    if not date_str:
        return None

    formats = [
        "%Y-%m-%d",
        "%d.%m.%Y",
        "%d/%m/%Y",
        "%Y/%m/%d",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue

    return None


def validate_vat_id(vat_id: str) -> bool:
    """
    Validate German VAT ID (USt-IdNr.).
    Format: DE123456789

    Args:
        vat_id: VAT ID to validate

    Returns:
        True if valid, False otherwise
    """
    if not vat_id:
        return False

    # Remove spaces and convert to uppercase
    vat_id = vat_id.replace(" ", "").upper()

    # German VAT ID pattern
    pattern = r"^DE\d{9}$"

    return bool(re.match(pattern, vat_id))


def calculate_vat(net_amount: float, vat_rate: float = 0.19) -> tuple[float, float]:
    """
    Calculate VAT amount and gross amount.

    Args:
        net_amount: Net amount (without VAT)
        vat_rate: VAT rate (default: 19% for Germany)

    Returns:
        Tuple of (vat_amount, gross_amount)
    """
    vat_amount = round(net_amount * vat_rate, 2)
    gross_amount = round(net_amount + vat_amount, 2)

    return vat_amount, gross_amount


def extract_net_from_gross(gross_amount: float, vat_rate: float = 0.19) -> tuple[float, float]:
    """
    Extract net amount and VAT from gross amount.

    Args:
        gross_amount: Gross amount (including VAT)
        vat_rate: VAT rate (default: 19% for Germany)

    Returns:
        Tuple of (net_amount, vat_amount)
    """
    net_amount = round(gross_amount / (1 + vat_rate), 2)
    vat_amount = round(gross_amount - net_amount, 2)

    return net_amount, vat_amount
