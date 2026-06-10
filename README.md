# codex-reconnecting-doctor

[中文文档](README.zh-CN.md)

Codex skill for diagnosing and repairing Codex Desktop reconnect loops caused by stale proxy settings, local proxy port changes, WebSocket/WSS failures, or provider transport mismatch.

Inspired by the ergonomics of mature `doctor` tools such as Homebrew `brew doctor`, Flutter `flutter doctor`, React Native Doctor, and Expo Doctor: report first, explain each finding, modify files only when explicitly requested, and produce output that can be shared in issues.

## Installation

There are two supported installation paths.

### 1. Install from the Codex Plugin Marketplace

Add this repository as a Codex plugin marketplace, then install the plugin from that marketplace:

```bash
codex plugin marketplace add baixinpan/codex-reconnecting-doctor
codex plugin add codex-reconnecting-doctor@codex-reconnecting-doctor
```

If the marketplace has already been added and you only want to refresh it, run:

```bash
codex plugin marketplace upgrade codex-reconnecting-doctor
```

You can also install through the Codex app UI after adding the marketplace: open **Plugins**, choose **Codex Reconnecting Doctor**, then install `codex-reconnecting-doctor`.

### 2. Install from Source

Clone the repository:

```bash
git clone https://github.com/baixinpan/codex-reconnecting-doctor.git
cd codex-reconnecting-doctor
```

For local skill development, copy or symlink the source skill into your Codex skills directory:

```bash
mkdir -p ~/.codex/skills
ln -s "$PWD" ~/.codex/skills/codex-reconnecting-doctor
```

For local plugin development, add the cloned repository as a local marketplace:

```bash
codex plugin marketplace add "$PWD"
codex plugin add codex-reconnecting-doctor@codex-reconnecting-doctor
```

Restart Codex Desktop after installing.

Note: OpenAI-curated public Plugin Directory publishing is not currently a self-serve flow. This repository is distributed as a public GitHub marketplace source and as source code.

## Use

Ask Codex:

```text
Use $codex-reconnecting-doctor to diagnose why Codex Desktop is stuck reconnecting.
```

The bundled script is safe by default:

```bash
python3 scripts/codex_reconnect_doctor.py
python3 scripts/codex_reconnect_doctor.py --json
python3 scripts/codex_reconnect_doctor.py --fix-env --dry-run
python3 scripts/codex_reconnect_doctor.py --fix-env
python3 scripts/codex_reconnect_doctor.py --disable-websockets
```

By default the report redacts sensitive-looking URL credentials and tokens. Use `--include-private` only for local debugging.

## What It Checks

- Codex home, `~/.codex/.env`, and `~/.codex/config.toml`.
- Active provider, base URL, direct provider reachability, and `supports_websockets`.
- Environment proxy variables, macOS system proxy, Windows/WSL environment proxy, listener processes, and common local proxy ports.
- HTTP CONNECT support before writing `HTTP_PROXY` or `HTTPS_PROXY`.
- Stale or missing proxy config and WebSocket fallback recommendations.

## Compatibility

- macOS Codex Desktop with Clash Verge/mihomo, Surge, sing-box, V2Ray/Xray, Loon, or system HTTP proxy.
- Linux environments with env proxies, `ss`/`lsof`, and HTTP-compatible local proxy clients.
- Windows/WSL diagnostics through environment variables and WSL-visible listeners, with manual confirmation for Windows-native proxy ports.

## Safety

- No files are changed unless `--fix-env` or `--disable-websockets` is provided.
- Use `--dry-run` to preview edits.
- Existing config files are backed up before modification.
- Proxy ports are verified with HTTP CONNECT before they are written.

## Repository Layout

```text
.agents/plugins/marketplace.json
plugins/codex-reconnecting-doctor/.codex-plugin/plugin.json
plugins/codex-reconnecting-doctor/skills/codex-reconnecting-doctor/SKILL.md
```

The root `SKILL.md` is kept for local skill development. The installable plugin copies the same skill under `plugins/codex-reconnecting-doctor/skills/`.

## License

MIT
