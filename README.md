# MCP Config Validator

[![ci](https://github.com/mohabdelkarim/mcp_config_validator/actions/workflows/ci.yml/badge.svg)](https://github.com/mohabdelkarim/mcp_config_validator/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)

**Free Cursor `mcp.json` validator** for Model Context Protocol (`mcpServers`) configs.

Catch broken MCP JSON before you restart the IDE: shell-string `command` values, `args` as a string instead of a list, empty commands, non-string `env` values, missing transport, and `http` URLs.

**Try it in the browser:** [mohabdelkarim.github.io/mcp_config_validator](https://mohabdelkarim.github.io/mcp_config_validator/)

From the creator of [AI Tool Drop](https://mohaabdelkarim.gumroad.com/) ·
[mohabdelkarim.com](https://www.mohabdelkarim.com/) ·
[@mohabdelkarim](https://github.com/mohabdelkarim)

## Why this exists

Cursor reads `.cursor/mcp.json` (project) or `~/.cursor/mcp.json` (global). A tiny JSON mistake often fails silently until you waste time restarting and reading MCP logs. This tool checks the shape of your config in seconds.

## Install

```bash
pip install git+https://github.com/mohabdelkarim/mcp_config_validator.git
```

Or from a clone:

```bash
pip install -e ".[dev]"
```

## CLI

```bash
mcp_config_validator path/to/mcp.json
mcp_config_validator .cursor/mcp.json
python -m mcp_config_validator path/to/mcp.json
type mcp.json | mcp_config_validator -
```

Exit code `0` when there are no errors. Use `--strict` to also fail on warnings.

### Common mistake it catches

Broken (one shell string in `command`):

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx -y @modelcontextprotocol/server-filesystem /tmp"
    }
  }
}
```

```text
ERROR server "filesystem": "command" looks like a full shell string; split into command + args ...
FAIL  1 server(s) checked, 1 error(s), 0 warning(s)
```

Fixed:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]
    }
  }
}
```

## What it checks

- Valid JSON
- Root object with `mcpServers`
- Each server is an object with a non-empty name
- Each server has `command` and/or `url`
- `command` is a non-empty string (not a full shell line without `args`)
- `args` is a list of strings
- `env` values are strings
- `url` should use `https` (`http` is a warning)

No network calls. It does not install packages or start MCP servers.

## Keywords

`cursor` · `mcp` · `mcp.json` · `mcpServers` · `model context protocol` · `json validator` · `cli`

## License

MIT © MOHAbdelkarim
