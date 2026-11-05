# MCP Config Validator

Catch broken Cursor MCP configs before you restart the IDE.

Paste or point at your `mcp.json`. Get clear errors and warnings for common
`mcpServers` mistakes: bad `args` types, empty commands, non-string `env`
values, missing transport, and `http` URLs.

From the creator of [AI Tool Drop](https://mohaabdelkarim.gumroad.com/) ·
[mohabdelkarim.com](https://www.mohabdelkarim.com/) ·
[@mohabdelkarim](https://github.com/mohabdelkarim)

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
python -m mcp_config_validator path/to/mcp.json
type mcp.json | mcp_config_validator -
```

Exit code `0` when there are no errors. Use `--strict` to also fail on warnings.

### Example

Broken config:

```json
{
  "mcpServers": {
    "browser": {
      "command": "npx",
      "args": "-y some-package"
    }
  }
}
```

Output:

```text
ERROR server "browser": "args" must be a list of strings (got str)
FAIL  1 server(s) checked, 1 error(s), 0 warning(s)
```

Fixed:

```json
{
  "mcpServers": {
    "browser": {
      "command": "npx",
      "args": ["-y", "some-package"]
    }
  }
}
```

## Browser UI

Open the GitHub Pages paste UI (after Pages is enabled):

https://mohabdelkarim.github.io/mcp_config_validator/

## What it checks

- Valid JSON
- Root object with `mcpServers`
- Each server is an object with a non-empty name
- Each server has `command` and/or `url`
- `command` is a non-empty string; `args` is a list of strings
- `env` values are strings
- `url` should use `https` (`http` is a warning)

No network calls. It does not install packages or start MCP servers.

## License

MIT © MOHAbdelkarim
