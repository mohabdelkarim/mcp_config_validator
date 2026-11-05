"""Validate Cursor MCP JSON configs."""

from __future__ import annotations

__version__ = "0.1.0"

from mcp_config_validator.validate import Finding, Severity, format_report, parse_and_validate, validate

__all__ = [
    "Finding",
    "Severity",
    "format_report",
    "parse_and_validate",
    "validate",
    "__version__",
]
