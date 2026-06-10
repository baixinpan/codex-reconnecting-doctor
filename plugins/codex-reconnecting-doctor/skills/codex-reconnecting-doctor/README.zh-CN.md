# codex-reconnecting-doctor

[English](README.md)

用于诊断和修复 Codex Desktop 反复 `Reconnecting`、窗口重连失败后不可用、代理端口变化、WebSocket/WSS 失败、provider transport 配置不匹配等问题的 Codex skill。

这个项目借鉴了成熟 `doctor` 工具的交互方式，例如 Homebrew `brew doctor`、Flutter `flutter doctor`、React Native Doctor 和 Expo Doctor：先诊断、逐项解释、只有明确要求时才修改文件，并尽量输出可以直接贴到 issue 里的报告。

## 安装

通过 Codex 的 skill installer 从 GitHub 安装，或者把整个目录复制到：

```bash
~/.codex/skills/codex-reconnecting-doctor
```

安装后需要完全重启 Codex Desktop，skill 才会被发现。

## 使用

在 Codex 里这样说：

```text
使用 $codex-reconnecting-doctor 帮我检查 Codex Desktop 一直 Reconnecting 的问题。
```

也可以用英文：

```text
Use $codex-reconnecting-doctor to diagnose why Codex Desktop is stuck reconnecting.
```

脚本默认是安全的，只做诊断：

```bash
python3 scripts/codex_reconnect_doctor.py
python3 scripts/codex_reconnect_doctor.py --json
python3 scripts/codex_reconnect_doctor.py --fix-env --dry-run
python3 scripts/codex_reconnect_doctor.py --fix-env
python3 scripts/codex_reconnect_doctor.py --disable-websockets
```

默认报告会脱敏 URL 中看起来像凭据、token、API key 的内容。只有本地排查时才使用 `--include-private`。

## 会检查什么

- Codex home、`~/.codex/.env`、`~/.codex/config.toml`。
- 当前 active provider、base URL、provider 直连可达性、`supports_websockets`。
- 环境变量代理、macOS 系统代理、Windows/WSL 环境变量代理、监听进程、常见本地代理端口。
- 写入 `HTTP_PROXY` / `HTTPS_PROXY` 前，先确认代理端口支持 HTTP CONNECT。
- 识别代理配置缺失、端口过期、WebSocket fallback 风险，并给出下一步建议。

## 兼容性

- macOS Codex Desktop：Clash Verge/mihomo、Surge、sing-box、V2Ray/Xray、Loon、系统 HTTP 代理。
- Linux：环境变量代理、`ss`/`lsof` 可见的本地 HTTP/mixed 代理。
- Windows/WSL：通过环境变量和 WSL 可见监听端口做诊断；Windows 原生代理端口可能需要人工确认。

## 安全策略

- 默认不修改任何文件。
- 只有传入 `--fix-env` 或 `--disable-websockets` 才会写配置。
- 使用 `--dry-run` 可以预览修改。
- 修改前会备份已有配置文件。
- 只有通过 HTTP CONNECT 验证的端口才会写入 `HTTP_PROXY` 和 `HTTPS_PROXY`。

## 常见处理路径

1. 先运行诊断：

```bash
python3 scripts/codex_reconnect_doctor.py
```

2. 如果报告显示找到了可用 HTTP/mixed 代理，但 `.env` 缺失或端口过期：

```bash
python3 scripts/codex_reconnect_doctor.py --fix-env --dry-run
python3 scripts/codex_reconnect_doctor.py --fix-env
```

3. 如果代理可达，但 Codex 仍然围绕 WebSocket/WSS 重连：

```bash
python3 scripts/codex_reconnect_doctor.py --disable-websockets --dry-run
python3 scripts/codex_reconnect_doctor.py --disable-websockets
```

4. 修改配置后，完全退出并重启 Codex Desktop。

## 许可证

MIT
