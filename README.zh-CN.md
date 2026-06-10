# codex-reconnecting-doctor

[English](README.md)

这是一个 Codex skill/plugin，用来诊断和修复 Codex Desktop 反复 `Reconnecting` 的问题。常见原因包括：代理端口变化、Codex 没有继承代理配置、WebSocket/WSS 连接失败、Codex 配置过期等。

默认情况下它只诊断、不改文件。只有你明确要求修复时，它才会写配置，并且会先备份。

## 适合谁

如果你遇到下面这些情况，可以安装这个工具：

- Codex Desktop 一直显示 `Reconnecting`；
- 每次回答前都要重连很多次；
- 某个窗口重连失败后再也不能用了；
- 必须开新窗口才能继续用；
- 换网络、代理软件重启、Codex 更新之后开始频繁报错。

## 推荐安装方式

最简单的方式是在 Codex 里直接安装 skill。把下面这句话粘贴到 Codex 聊天框：

```text
Use $skill-installer to install https://github.com/baixinpan/codex-reconnecting-doctor/tree/main/plugins/codex-reconnecting-doctor/skills/codex-reconnecting-doctor
```

安装后重启 Codex Desktop。

这种方式不要求你的终端里有 `codex` 命令。

## 使用

安装后，在 Codex 里这样说：

```text
使用 $codex-reconnecting-doctor 帮我检查 Codex Desktop 一直 Reconnecting 的问题。
```

如果你希望它自动修复，可以这样说：

```text
使用 $codex-reconnecting-doctor 诊断并修复我的 Codex Desktop 重连问题。
```

Codex 会运行插件内置的诊断脚本，展示检测证据，并告诉你是否需要重启 Codex Desktop。

## 可选：作为插件安装

如果你的终端里已经有 `codex` CLI，并且希望通过 Codex plugin 系统安装，可以使用这种方式。

在系统终端里运行：

```bash
codex plugin marketplace add baixinpan/codex-reconnecting-doctor
codex plugin add codex-reconnecting-doctor@codex-reconnecting-doctor
```

如果 macOS 终端提示 `codex: command not found`，可以使用 Codex Desktop 自带的 CLI 路径：

```bash
/Applications/Codex.app/Contents/Resources/codex plugin marketplace add baixinpan/codex-reconnecting-doctor
/Applications/Codex.app/Contents/Resources/codex plugin add codex-reconnecting-doctor@codex-reconnecting-doctor
```

安装后重启 Codex Desktop。

注意：这个插件不能在默认 OpenAI-curated 插件市场里直接搜索到。只有先添加这个 GitHub 仓库作为 marketplace source，才会在 Codex Plugins 里出现。

## 更新

如果是用 `$skill-installer` 安装的，在 Codex 里重新安装同一个 GitHub URL 即可。

如果是作为插件安装的，在终端里运行：

```bash
codex plugin marketplace upgrade codex-reconnecting-doctor
codex plugin add codex-reconnecting-doctor@codex-reconnecting-doctor
```

## 卸载

如果是作为 skill 安装的，删除 Codex skills 目录里的 skill 文件夹，然后重启 Codex：

```bash
rm -rf ~/.codex/skills/codex-reconnecting-doctor
```

如果是作为插件安装的，运行：

```bash
codex plugin remove codex-reconnecting-doctor@codex-reconnecting-doctor
```

## 它会检查什么

- `~/.codex/.env` 里的代理环境变量。
- `~/.codex/config.toml` 里的当前 provider 配置。
- 本机 HTTP / mixed 代理端口。
- macOS 系统代理设置。
- Linux 和 WSL 的代理环境变量。
- 代理端口是否真的支持 HTTP CONNECT。
- 当前 provider 是否可能需要 `supports_websockets = false`。

## 安全策略

- 默认只诊断，不修改文件。
- 只有明确要求修复时才会写代理配置。
- 修改已有文件前会先备份。
- 写入 `HTTP_PROXY` 或 `HTTPS_PROXY` 前，会先验证代理端口。
- 默认会脱敏报告里看起来像凭据、token、API key 的内容。

## 高级：使用源码

大多数用户应该使用 `$skill-installer` 安装。

只有在你想检查代码、修改代码、或手动运行诊断脚本时，才需要 clone 源码：

```bash
git clone https://github.com/baixinpan/codex-reconnecting-doctor.git
cd codex-reconnecting-doctor
```

直接运行诊断脚本：

```bash
python3 scripts/codex_reconnect_doctor.py
python3 scripts/codex_reconnect_doctor.py --json
python3 scripts/codex_reconnect_doctor.py --fix-env --dry-run
python3 scripts/codex_reconnect_doctor.py --fix-env
python3 scripts/codex_reconnect_doctor.py --disable-websockets --dry-run
python3 scripts/codex_reconnect_doctor.py --disable-websockets
```

## 分发说明

这个仓库同时支持通过 `$skill-installer` 直接安装 skill，也支持通过公开 GitHub marketplace source 安装 plugin。OpenAI-curated 公共插件目录目前不是自助上架流程。

## 许可证

MIT
