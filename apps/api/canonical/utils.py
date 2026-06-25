from datetime import datetime
from decimal import Decimal, InvalidOperation


def parse_decimal(value: object, default: Decimal | None = None) -> Decimal | None:
    if value is None or str(value).strip() == "":
        return default
    try:
        return Decimal(str(value).replace(",", "").strip())
    except (InvalidOperation, ValueError):
        return default


def parse_int(value: object, default: int | None = None) -> int | None:
    if value is None or str(value).strip() == "":
        return default
    try:
        return int(float(str(value)))
    except (ValueError, TypeError):
        return default


def parse_date(value: object) -> datetime | None:
    if value is None or str(value).strip() == "":
        return None
    if isinstance(value, datetime):
        return value
    text = str(value).strip()[:19]
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%m/%d/%Y"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    return None


def parse_bool(value: object, default: bool = True) -> bool:
    if value is None or str(value).strip() == "":
        return default
    text = str(value).strip().lower()
    if text in ("true", "1", "yes", "active"):
        return True
    if text in ("false", "0", "no", "inactive"):
        return False
    return default


def safe_str(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text if text else None
