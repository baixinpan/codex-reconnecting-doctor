# Compatibility Notes

## Platform Support

| Platform | Detection level | Notes |
| --- | --- | --- |
| macOS | Full | Uses `scutil --proxy`, `lsof`, `netstat`, environment variables, and curl CONNECT verification. |
| Linux | Good | Uses environment variables, `ss` or `lsof`, common proxy process names, common proxy ports, and curl CONNECT verification. |
| Windows/WSL | Partial | Uses environment variables and WSL-visible listeners. Windows-native proxy app ports may need manual confirmation or `--proxy-port`. |

## Proxy Clients

The skill is designed for HTTP or mixed local proxy ports from:

- Clash Verge / verge-mihomo / mihomo / Clash.Meta
- Surge
- sing-box
- V2Ray / Xray
- Loon
- HTTP-compatible custom local proxy tools

The script also probes common local proxy ports. This helps on machines where process names are hidden, localized, or unavailable. Use `--no-common-ports` for a stricter report.

SOCKS-only ports are not written to `HTTP_PROXY` or `HTTPS_PROXY`. If a SOCKS port is the only working option, use `ALL_PROXY=socks5://127.0.0.1:<port>` only after verifying the user's environment supports it.

## Common Port Pitfalls

Do not assume these ports are HTTP proxies:

- Clash Verge dashboard, API, or control ports.
- Local development servers such as `8080`.
- Browser remote debugging ports.
- App-specific helper ports from chat, IDE, sync, or mobile tooling.

Always require an HTTP CONNECT test before writing `HTTP_PROXY` and `HTTPS_PROXY`.

## Report Modes

- Human report: default output, suitable for terminal diagnosis.
- JSON report: use `--json` for issue templates, CI, or other tooling.
- Private report: use `--include-private` only on trusted machines; default output redacts sensitive-looking tokens and URL credentials.

## WebSocket Fallback

Some proxies and relays allow normal HTTPS but fail WebSocket/WSS or long-lived streaming connections. When Codex repeatedly reconnects even though HTTPS to the provider works, set this in the active provider block:

```toml
supports_websockets = false
```

This should be placed under the provider selected by top-level `model_provider`, not under an unused provider.

## Publishing Checklist

- Keep the skill name `codex-reconnecting-doctor`.
- Keep the repository root installable as a Codex skill: `SKILL.md` must stay at the repository root.
- Run `python3 scripts/codex_reconnect_doctor.py --dry-run` before release.
- Run the skill validator from the Codex `skill-creator` system skill.
- Do not include private proxy endpoints, tokens, user paths, or machine-specific config in examples.
