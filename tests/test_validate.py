"""Tests for MCP config validation rules."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from mcp_config_validator.validate import Finding, Severity, parse_and_validate, validate

FIXTURES = Path(__file__).parent / "fixtures"


def _load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def _codes(findings: list[Finding]) -> list[str]:
    return [f.code for f in findings]


def test_valid_basic_has_no_errors() -> None:
    findings = validate(_load("valid_basic.json"))
    assert not any(f.severity == Severity.ERROR for f in findings)


def test_bad_args_type_is_error() -> None:
    findings = validate(_load("bad_args_type.json"))
    assert any(f.code == "args_type" and f.severity == Severity.ERROR for f in findings)
    browser = next(f for f in findings if f.code == "args_type")
    assert 'server "browser"' in browser.message


def test_missing_mcpservers_is_error() -> None:
    findings = validate(_load("missing_mcpservers.json"))
    assert "missing_mcp_servers" in _codes(findings)


def test_empty_command_is_error() -> None:
    findings = validate(_load("empty_command.json"))
    assert "empty_command" in _codes(findings)


def test_env_non_string_is_error() -> None:
    findings = validate(_load("env_non_string.json"))
    assert "env_value_type" in _codes(findings)


def test_http_url_is_warning() -> None:
    findings = validate(_load("http_url.json"))
    assert any(f.code == "url_http" and f.severity == Severity.WARNING for f in findings)


def test_command_shell_string_is_error() -> None:
    findings = validate(_load("command_shell_string.json"))
    assert any(
        f.code == "command_shell_string" and f.severity == Severity.ERROR for f in findings
    )


def test_root_must_be_object() -> None:
    findings = validate(["not", "an", "object"])  # type: ignore[arg-type]
    assert "root_type" in _codes(findings)


def test_server_must_be_object() -> None:
    findings = validate({"mcpServers": {"x": "bad"}})
    assert "server_type" in _codes(findings)


def test_whitespace_server_name_is_error() -> None:
    findings = validate({"mcpServers": {"   ": {"command": "npx", "args": ["x"]}}})
    assert "server_name" in _codes(findings)


def test_missing_command_and_url_is_error() -> None:
    findings = validate({"mcpServers": {"x": {"env": {"A": "1"}}}})
    assert "missing_transport" in _codes(findings)


def test_parse_and_validate_invalid_json() -> None:
    findings = parse_and_validate("{not json")
    assert findings[0].code == "invalid_json"
    assert findings[0].severity == Severity.ERROR


def test_parse_and_validate_valid_json() -> None:
    raw = (FIXTURES / "valid_basic.json").read_text(encoding="utf-8")
    findings = parse_and_validate(raw)
    assert not any(f.severity == Severity.ERROR for f in findings)


def test_format_report_contains_summary() -> None:
    from mcp_config_validator.validate import format_report

    findings = validate(_load("bad_args_type.json"))
    report = format_report(findings, server_count=1)
    assert "ERROR" in report
    assert "server(s) checked" in report
