# codex-reconnecting-doctor

[中文文档](README.zh-CN.md)

A Codex skill/plugin that helps diagnose and repair Codex Desktop `Reconnecting` loops caused by proxy changes, broken proxy inheritance, WebSocket/WSS transport failures, or stale Codex configuration.

The doctor is safe by default: it reports first, explains what it found, and only changes files when you explicitly ask it to.

## Who This Is For

Use this if Codex Desktop:

- keeps showing `Reconnecting`;
- reconnects several times before answering;
- opens a window that never recovers after a reconnect failure;
- works only after you open a new window;
- started failing after your proxy app, network, or Codex version changed.

## Recommended Install

The easiest way is to install the skill from inside Codex. Paste this into the Codex chat box:

```text
Use $skill-installer to install https://github.com/baixinpan/codex-reconnecting-doctor/tree/main/plugins/codex-reconnecting-doctor/skills/codex-reconnecting-doctor
```

Restart Codex Desktop after installation.

This path does not require the `codex` command to be available in your terminal.

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

## Alternative: Install as a Plugin

Use this if you already have the `codex` CLI available in Terminal and want to install through the Codex plugin system.

Run in your system terminal:

```bash
codex plugin marketplace add baixinpan/codex-reconnecting-doctor
codex plugin add codex-reconnecting-doctor@codex-reconnecting-doctor
```

If Terminal says `codex: command not found` on macOS, use the Codex Desktop bundled CLI:

```bash
/Applications/Codex.app/Contents/Resources/codex plugin marketplace add baixinpan/codex-reconnecting-doctor
/Applications/Codex.app/Contents/Resources/codex plugin add codex-reconnecting-doctor@codex-reconnecting-doctor
```

Restart Codex Desktop after installation.

Note: this plugin is not searchable in the default OpenAI-curated Plugin Directory. It appears in Codex Plugins only after you add this GitHub repository as a marketplace source.

## Update

If installed with `$skill-installer`, ask Codex to reinstall the same GitHub URL.

If installed as a plugin, run in Terminal:

```bash
codex plugin marketplace upgrade codex-reconnecting-doctor
codex plugin add codex-reconnecting-doctor@codex-reconnecting-doctor
```

## Uninstall

If installed as a skill, remove the skill folder from your Codex skills directory, then restart Codex:

```bash
rm -rf ~/.codex/skills/codex-reconnecting-doctor
```

If installed as a plugin, run:

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

## Advanced: Source Usage

Most users should install through `$skill-installer`.

Use source only if you want to inspect, modify, or run the doctor script manually:

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

This repository supports both direct skill installation through `$skill-installer` and plugin installation through a public GitHub marketplace source. OpenAI-curated public Plugin Directory publishing is not currently a self-serve flow.

## License

MIT
