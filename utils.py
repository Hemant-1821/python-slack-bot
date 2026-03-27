from __future__ import annotations

from typing import Any

from constants import db_keywords


def is_db_related_message(msg: str) -> bool:
    lower = msg.lower()
    return any(keyword in lower for keyword in db_keywords)


def _js_type_name(value: Any) -> str:
    if value is None:
        return "unknown-type"
    if isinstance(value, list):
        return "array"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, (int, float)):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, dict):
        return "object"
    return "object"


def get_schema_structure(obj: Any) -> Any:
    """Return shallow schema type mapping, mirroring the JS helper behavior."""
    if not isinstance(obj, dict):
        return {}

    struct: dict[str, str] = {}
    for key, value in obj.items():
        struct[key] = _js_type_name(value)
    return struct

