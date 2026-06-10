# codex-reconnecting-doctor

[中文文档](README.zh-CN.md)

A Codex plugin that helps diagnose and repair Codex Desktop `Reconnecting` loops caused by proxy changes, broken proxy inheritance, WebSocket/WSS transport failures, or stale Codex configuration.

The doctor is safe by default: it reports first, explains what it found, and only changes files when you explicitly ask it to.

## Who This Is For

Use this if Codex Desktop:

- keeps showing `Reconnecting`;
- reconnects several times before answering;
- opens a window that never recovers after a reconnect failure;
- works only after you open a new window;
- started failing after your proxy app, network, or Codex version changed.

## Install

Run these commands in your system terminal

On macOS, open **Terminal.app**. On Linux or WSL, open your normal shell.

```bash
codex plugin marketplace add baixinpan/codex-reconnecting-doctor
codex plugin add codex-reconnecting-doctor@codex-reconnecting-doctor
```

Then restart Codex Desktop.

If you prefer the app UI, run only the first command in Terminal, then open Codex **Plugins**, choose **Codex Reconnecting Doctor**, and install it there.

## Use

After installation, ask Codex:

```text
Use $codex-reconnecting-doctor to diagnose why Codex Desktop is stuck reconnecting.
```

For an automatic repair, ask:

```text
Use $codex-reconnecting-doctor to diagnose and fix my Codex Desktop reconnecting issue.
```

Codex will run the bundled doctor script, show the evidence, and explain whether you need to restart Codex Desktop.

## Update

Run these commands in Terminal:

```bash
codex plugin marketplace upgrade codex-reconnecting-doctor
codex plugin add codex-reconnecting-doctor@codex-reconnecting-doctor
```

Restart Codex Desktop after updating.

## Uninstall

Run this in Terminal:

```bash
codex plugin remove codex-reconnecting-doctor@codex-reconnecting-doctor
```

## What It Checks

- `~/.codex/.env` proxy variables.
- `~/.codex/config.toml` active provider settings.
- Local HTTP and mixed proxy ports.
- macOS system proxy settings.
- Linux and WSL environment proxy variables.
- Whether a proxy port really supports HTTPS tunneling with HTTP CONNECT.
- Whether the active provider may need `supports_websockets = false`.

## Safety

- The default diagnosis does not modify files.
- Proxy settings are written only when repair is explicitly requested.
- Existing files are backed up before modification.
- Ports are tested before being written to `HTTP_PROXY` or `HTTPS_PROXY`.
- Reports redact sensitive-looking URL credentials and tokens by default.

## Advanced: Source Install

Most users should use the plugin install above.

Use source install only if you want to inspect, modify, or run the project manually:

```bash
git clone https://github.com/baixinpan/codex-reconnecting-doctor.git
cd codex-reconnecting-doctor
```

Run the doctor script directly:

```bash
python3 scripts/codex_reconnect_doctor.py
python3 scripts/codex_reconnect_doctor.py --json
python3 scripts/codex_reconnect_doctor.py --fix-env --dry-run
python3 scripts/codex_reconnect_doctor.py --fix-env
python3 scripts/codex_reconnect_doctor.py --disable-websockets --dry-run
python3 scripts/codex_reconnect_doctor.py --disable-websockets
```

## Distribution Notes

This repository is a public Codex plugin marketplace source. OpenAI-curated public Plugin Directory publishing is not currently a self-serve flow, so users install this plugin by adding this GitHub repository as a marketplace source.

## License

MIT
