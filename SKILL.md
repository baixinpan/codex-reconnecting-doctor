---
name: codex-reconnecting-doctor
description: Diagnose and repair Codex Desktop reconnect loops, unusable windows after "Reconnecting", stream disconnected errors, and proxy/WebSocket transport failures. Use when Codex Desktop on macOS, Linux, or Windows/WSL needs local proxy detection, ~/.codex/.env proxy repair, provider transport checks, or supports_websockets=false configuration for Clash Verge/mihomo, Surge, sing-box, V2Ray/Xray, Loon, or other HTTP/mixed proxies.
---

# Codex Desktop Reconnect Doctor

## Overview

Use this skill to restore Codex Desktop connectivity without guessing proxy ports or blindly rewriting user config. Treat reconnect loops as a transport-path problem first: proxy inheritance, WSS/WebSocket support, active provider selection, and stale Desktop process state.

## Quick Start

Run the bundled doctor script first:

```bash
python3 scripts/codex_reconnect_doctor.py
```

Use JSON output when the user wants to paste diagnostics into an issue, compare machines, or automate checks:

```bash
python3 scripts/codex_reconnect_doctor.py --json
```

If the report identifies a verified HTTP or mixed proxy port, update `~/.codex/.env` while preserving unrelated lines:

```bash
python3 scripts/codex_reconnect_doctor.py --fix-env
```

If WebSocket/WSS appears to be the failure mode, disable WebSocket for the active provider:

```bash
python3 scripts/codex_reconnect_doctor.py --disable-websockets
```

Use `--dry-run` with either modifying command to preview the exact actions.

The script redacts sensitive-looking credentials by default. Use `--include-private` only on trusted machines. Use `--proxy-port <port>` when a user's proxy client is hidden from listener detection, and `--no-common-ports` when the user wants a stricter report.

## Workflow

1. Inspect the current failure.
   - Look for `Reconnecting`, repeated reconnect attempts, `stream disconnected`, WebSocket/WSS failures, or a window that cannot recover until a new window is opened.
   - Check whether Codex recently updated, the proxy app restarted, the proxy mode changed, or the machine moved networks.

2. Run the doctor script.
   - Prefer the script over manual port guessing.
   - Read the report sections: Codex files, active provider, proxy candidates, verified proxy, and recommendations.
   - A proxy candidate must pass an HTTP CONNECT test before it is used for `HTTP_PROXY`/`HTTPS_PROXY`.
   - Use `--json` for shareable diagnostics, keeping default redaction enabled.

3. Repair the smallest confirmed issue.
   - Use `--fix-env` when Codex has no usable proxy variables, the stored port is stale, or a better verified HTTP/mixed proxy is found.
   - Use `--disable-websockets` when HTTPS reaches the provider but Codex still reconnects around WSS/WebSocket transport.
   - Do not write Clash Verge control ports, REST API ports, dashboard ports, or random localhost app ports into `.env`.

4. Verify the result.
   - Confirm `.env` contains English colons, not full-width punctuation.
   - Confirm the selected proxy port still passes CONNECT.
   - Confirm `supports_websockets = false` is in the active provider block when WebSocket fallback is required.

5. Restart Codex Desktop.
   - Tell the user to fully quit Codex Desktop with `Cmd+Q` on macOS or equivalent app quit on other platforms.
   - Reopen Codex after file changes; existing processes may keep stale environment/config.

## Manual Checks

When the script cannot run, use these checks.

```bash
[ -f ~/.codex/.env ] && sed -n '1,120p' ~/.codex/.env || echo "NO ~/.codex/.env"
rg -n 'model_provider|^\[model_providers\.|base_url|wire_api|supports_websockets' ~/.codex/config.toml 2>/dev/null || true
```

macOS proxy and listener checks:

```bash
scutil --proxy
lsof -nP -iTCP -sTCP:LISTEN | rg -i 'clash|verge|mihomo|surge|sing|v2ray|xray|loon|proxy|127\.0\.0\.1'
```

Linux checks:

```bash
env | rg -i '^(http|https|all|no)_proxy=' || true
ss -ltnp | rg -i 'clash|verge|mihomo|surge|sing|v2ray|xray|proxy|127\.0\.0\.1' || true
```

HTTP proxy verification:

```bash
curl -I --max-time 12 -x http://127.0.0.1:<port> https://api.openai.com
```

`HTTP/1.1 200 Connection established` proves the local HTTP/mixed proxy can tunnel HTTPS. A following `401`, `404`, `421`, or provider-specific response can still be acceptable for transport verification.

## Config Rules

For `~/.codex/.env`, preserve unrelated lines and update only proxy keys:

```env
HTTP_PROXY="http://127.0.0.1:<verified-http-or-mixed-port>"
HTTPS_PROXY="http://127.0.0.1:<verified-http-or-mixed-port>"
http_proxy="http://127.0.0.1:<verified-http-or-mixed-port>"
https_proxy="http://127.0.0.1:<verified-http-or-mixed-port>"
```

For `~/.codex/config.toml`, edit the block selected by the top-level `model_provider`:

```toml
[model_providers.<active-provider>]
wire_api = "responses"
supports_websockets = false
```

Do not copy a provider block from another machine unless the base URL, auth mode, and provider name match the user's actual setup.

## Compatibility

See `references/compatibility.md` before changing behavior for another platform or proxy client.

Supported targets:
- macOS Codex Desktop with Clash Verge/mihomo, Surge, sing-box, V2Ray/Xray, Loon, or system HTTP proxy.
- Linux desktop or server environments using env proxies, `ss`, `lsof`, Clash/mihomo, sing-box, V2Ray/Xray, or HTTP-compatible local proxies.
- Windows/WSL diagnostics through env proxies and WSL-visible listeners, with manual Windows proxy confirmation or `--proxy-port` if listener ownership is not visible.

## Project Docs

For user-facing installation and publishing notes, keep both README files in sync:
- `README.md` for English.
- `README.zh-CN.md` for Simplified Chinese.

## Reporting

Report evidence, not guesses:
- Codex home path.
- Active provider and base URL when visible.
- Verified proxy port, process, and CONNECT result.
- Files changed and backup paths.
- Whether Codex Desktop must be restarted.
