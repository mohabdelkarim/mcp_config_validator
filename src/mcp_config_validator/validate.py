"""MCP config validation rules (Cursor mcpServers shape).

Rule ids (keep in sync with docs/index.html):
  invalid_json, root_type, missing_mcp_servers, mcp_servers_type,
  server_name, server_type, missing_transport, empty_command, command_type,
  command_shell_string, args_type, args_item_type, env_type, env_value_type,
  url_type, url_http
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from typing import Any


class Severity(str, Enum):
    ERROR = "ERROR"
    WARNING = "WARN"


@dataclass(frozen=True)
class Finding:
    severity: Severity
    code: str
    message: str


def parse_and_validate(raw: str) -> list[Finding]:
    """Parse JSON text then validate the resulting config."""
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        return [
            Finding(
                Severity.ERROR,
                "invalid_json",
                f"invalid JSON: {exc.msg} (line {exc.lineno}, column {exc.colno})",
            )
        ]
    return validate(data)


def validate(config: Any) -> list[Finding]:
    """Validate a parsed Cursor MCP config object."""
    findings: list[Finding] = []

    if not isinstance(config, dict):
        findings.append(
            Finding(Severity.ERROR, "root_type", "root value must be a JSON object")
        )
        return findings

    if "mcpServers" not in config:
        findings.append(
            Finding(
                Severity.ERROR,
                "missing_mcp_servers",
                'missing required key "mcpServers"',
            )
        )
        return findings

    servers = config["mcpServers"]
    if not isinstance(servers, dict):
        findings.append(
            Finding(
                Severity.ERROR,
                "mcp_servers_type",
                '"mcpServers" must be an object of named servers',
            )
        )
        return findings

    for name, server in servers.items():
        findings.extend(_validate_server(str(name), server))

    return findings


def _validate_server(name: str, server: Any) -> list[Finding]:
    findings: list[Finding] = []
    label = f'server "{name}"'

    if not name.strip():
        findings.append(
            Finding(
                Severity.ERROR,
                "server_name",
                f"{label}: server name must be non-empty (not whitespace only)",
            )
        )

    if not isinstance(server, dict):
        findings.append(
            Finding(
                Severity.ERROR,
                "server_type",
                f"{label}: value must be an object",
            )
        )
        return findings

    command = server.get("command")
    url = server.get("url")
    has_command = command is not None
    has_url = url is not None

    if not has_command and not has_url:
        findings.append(
            Finding(
                Severity.ERROR,
                "missing_transport",
                f'{label}: must set "command" or "url"',
            )
        )

    if has_command:
        if not isinstance(command, str):
            findings.append(
                Finding(
                    Severity.ERROR,
                    "command_type",
                    f'{label}: "command" must be a string (got {type(command).__name__})',
                )
            )
        elif not command.strip():
            findings.append(
                Finding(
                    Severity.ERROR,
                    "empty_command",
                    f'{label}: "command" must be a non-empty string',
                )
            )
        elif " " in command.strip() and "args" not in server:
            findings.append(
                Finding(
                    Severity.ERROR,
                    "command_shell_string",
                    f'{label}: "command" looks like a full shell string; '
                    'split into command + args '
                    '(example: command "npx", args ["-y", "package"])',
                )
            )

        if "args" in server:
            args = server["args"]
            if not isinstance(args, list):
                findings.append(
                    Finding(
                        Severity.ERROR,
                        "args_type",
                        f'{label}: "args" must be a list of strings '
                        f"(got {type(args).__name__})",
                    )
                )
            else:
                for idx, item in enumerate(args):
                    if not isinstance(item, str):
                        findings.append(
                            Finding(
                                Severity.ERROR,
                                "args_item_type",
                                f'{label}: "args[{idx}]" must be a string '
                                f"(got {type(item).__name__})",
                            )
                        )

    if has_url:
        if not isinstance(url, str):
            findings.append(
                Finding(
                    Severity.ERROR,
                    "url_type",
                    f'{label}: "url" must be a string (got {type(url).__name__})',
                )
            )
        elif url.startswith("http://"):
            findings.append(
                Finding(
                    Severity.WARNING,
                    "url_http",
                    f'{label}: "url" uses http; prefer https',
                )
            )
        elif not url.startswith("https://"):
            findings.append(
                Finding(
                    Severity.ERROR,
                    "url_type",
                    f'{label}: "url" must start with https:// (or http://)',
                )
            )

    if "env" in server:
        env = server["env"]
        if not isinstance(env, dict):
            findings.append(
                Finding(
                    Severity.ERROR,
                    "env_type",
                    f'{label}: "env" must be an object (got {type(env).__name__})',
                )
            )
        else:
            for key, value in env.items():
                if not isinstance(value, str):
                    findings.append(
                        Finding(
                            Severity.ERROR,
                            "env_value_type",
                            f'{label}: "env.{key}" must be a string '
                            f"(got {type(value).__name__})",
                        )
                    )

    return findings


def format_report(findings: list[Finding], server_count: int | None = None) -> str:
    """Render findings as a human-readable CLI report."""
    lines: list[str] = []
    for finding in findings:
        lines.append(f"{finding.severity.value:<5} {finding.message}")

    errors = sum(1 for f in findings if f.severity == Severity.ERROR)
    warnings = sum(1 for f in findings if f.severity == Severity.WARNING)
    checked = server_count if server_count is not None else _infer_server_count(findings)
    status = "OK" if errors == 0 else "FAIL"
    lines.append(
        f"{status:<5} {checked} server(s) checked, {errors} error(s), {warnings} warning(s)"
    )
    return "\n".join(lines)


def _infer_server_count(findings: list[Finding]) -> int:
    # Best-effort: count distinct server labels in messages when unknown.
    names: set[str] = set()
    for finding in findings:
        if 'server "' in finding.message:
            start = finding.message.find('server "') + len('server "')
            end = finding.message.find('"', start)
            if end > start:
                names.add(finding.message[start:end])
    return len(names)


def count_servers(config: Any) -> int:
    """Return number of entries under mcpServers when present."""
    if isinstance(config, dict) and isinstance(config.get("mcpServers"), dict):
        return len(config["mcpServers"])
    return 0
