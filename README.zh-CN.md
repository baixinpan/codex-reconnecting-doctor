# codex-reconnecting-doctor

[English](README.md)

用于诊断和修复 Codex Desktop 反复 `Reconnecting`、窗口重连失败后不可用、代理端口变化、WebSocket/WSS 失败、provider transport 配置不匹配等问题的 Codex skill。

这个项目借鉴了成熟 `doctor` 工具的交互方式，例如 Homebrew `brew doctor`、Flutter `flutter doctor`、React Native Doctor 和 Expo Doctor：先诊断、逐项解释、只有明确要求时才修改文件，并尽量输出可以直接贴到 issue 里的报告。

## 安装

只推荐两种安装路径。

### 1. 通过 Codex 插件市场安装

把这个 GitHub 仓库添加为 Codex 插件市场，然后从这个市场安装插件：

```bash
codex plugin marketplace add baixinpan/codex-reconnecting-doctor
codex plugin add codex-reconnecting-doctor@codex-reconnecting-doctor
```

如果已经添加过市场，只是想刷新插件列表，再运行：

```bash
codex plugin marketplace upgrade codex-reconnecting-doctor
```

也可以添加 marketplace 后，在 Codex app 里打开 **Plugins**，选择 **Codex Reconnecting Doctor**，再安装 `codex-reconnecting-doctor`。

### 2. 使用源码安装

先 clone 仓库：

```bash
git clone https://github.com/baixinpan/codex-reconnecting-doctor.git
cd codex-reconnecting-doctor
```

如果是本地开发 skill，可以把源码目录复制或软链接到 Codex skills 目录：

```bash
mkdir -p ~/.codex/skills
ln -s "$PWD" ~/.codex/skills/codex-reconnecting-doctor
```

如果是本地开发 plugin，可以把 clone 下来的仓库作为本地 marketplace 添加：

```bash
codex plugin marketplace add "$PWD"
codex plugin add codex-reconnecting-doctor@codex-reconnecting-doctor
```

安装后重启 Codex Desktop。

说明：OpenAI-curated 公共插件目录目前不是自助上架流程。这个项目通过公开 GitHub marketplace 源和源码两种方式分发。

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

## 仓库结构

```text
.agents/plugins/marketplace.json
plugins/codex-reconnecting-doctor/.codex-plugin/plugin.json
plugins/codex-reconnecting-doctor/skills/codex-reconnecting-doctor/SKILL.md
```

根目录 `SKILL.md` 用于本地 skill 开发。真正作为插件安装时，会使用 `plugins/codex-reconnecting-doctor/skills/` 下的同名 skill。

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
