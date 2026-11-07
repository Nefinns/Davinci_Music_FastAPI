from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Any

from bson import Decimal128, ObjectId


def clean_bson(value: Any) -> Any:
    """Convert BSON to a JSON-safe representation without lossy monetary floats."""
    if isinstance(value, ObjectId):
        return str(value)
    if isinstance(value, Decimal128):
        return str(value.to_decimal())
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat().replace('+00:00', 'Z') if value.tzinfo else value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): clean_bson(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [clean_bson(v) for v in value]
    if isinstance(value, bytes):
        return '<datos binarios>'
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)
