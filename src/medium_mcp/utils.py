"""
General utility functions for the Medium MCP package.
"""

from typing import Any


def safe_getattr(obj: Any, attr: str, default: Any) -> Any:
    """Get attribute safely, ensuring non-None return for required fields."""
    value = getattr(obj, attr, default)
    if value is None:
        return default
    return value
