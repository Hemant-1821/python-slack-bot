from __future__ import annotations
from typing import Any

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

