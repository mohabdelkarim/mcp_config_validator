"""CLI entry point for mcp_config_validator."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from mcp_config_validator.validate import (
    Severity,
    count_servers,
    format_report,
    parse_and_validate,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mcp_config_validator",
        description="Validate Cursor MCP JSON configs (mcpServers).",
    )
    parser.add_argument(
        "path",
        nargs="?",
        help="Path to mcp.json (reads stdin when omitted or set to -)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors for the exit code",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(list(argv) if argv is not None else None)

    if args.path and args.path != "-":
        path = Path(args.path)
        try:
            raw = path.read_text(encoding="utf-8")
        except OSError as exc:
            print(f"ERROR could not read {path}: {exc}", file=sys.stderr)
            return 1
    else:
        raw = sys.stdin.read()

    findings = parse_and_validate(raw)
    server_count = 0
    try:
        parsed = json.loads(raw)
        server_count = count_servers(parsed)
    except json.JSONDecodeError:
        server_count = 0

    print(format_report(findings, server_count=server_count))

    errors = sum(1 for f in findings if f.severity == Severity.ERROR)
    warnings = sum(1 for f in findings if f.severity == Severity.WARNING)
    if errors:
        return 1
    if args.strict and warnings:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
