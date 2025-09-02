"""
String and data formatting functions for the Medium MCP package.
"""

from typing import Any


def normalize_tag(tag: str) -> str:
    """Convert user input tag to Medium API format (lowercase with hyphens)."""
    if not tag:
        return tag
    return tag.lower().replace(" ", "-")


def convert_to_string(value: Any) -> str:
    """Convert various value types to strings safely."""
    if value is None or value == "":
        return ""
    elif hasattr(value, "username") and value.username:
        return str(value.username)
    elif hasattr(value, "isoformat"):
        return value.isoformat()
    else:
        return str(value) if value else ""
