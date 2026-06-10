# codex-reconnecting-doctor

[English](README.md)

这是一个 Codex 插件，用来诊断和修复 Codex Desktop 反复 `Reconnecting` 的问题。常见原因包括：代理端口变化、Codex 没有继承代理配置、WebSocket/WSS 连接失败、Codex 配置过期等。

默认情况下它只诊断、不改文件。只有你明确要求修复时，它才会写配置，并且会先备份。

## 适合谁

如果你遇到下面这些情况，可以安装这个插件：

- Codex Desktop 一直显示 `Reconnecting`；
- 每次回答前都要重连很多次；
- 某个窗口重连失败后再也不能用了；
- 必须开新窗口才能继续用；
- 换网络、代理软件重启、Codex 更新之后开始频繁报错。

## 安装

下面的命令是在系统终端里输入

macOS 打开 **Terminal.app**。Linux 或 WSL 打开你平时用的 shell。

```bash
codex plugin marketplace add baixinpan/codex-reconnecting-doctor
codex plugin add codex-reconnecting-doctor@codex-reconnecting-doctor
```

安装后重启 Codex Desktop。

如果你想用 Codex App 界面安装：先在终端里运行第一条命令，然后打开 Codex 的 **Plugins** 页面，选择 **Codex Reconnecting Doctor**，再安装插件。

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

## 更新

在终端里运行：

```bash
codex plugin marketplace upgrade codex-reconnecting-doctor
codex plugin add codex-reconnecting-doctor@codex-reconnecting-doctor
```

更新后重启 Codex Desktop。

## 卸载

在终端里运行：

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

大多数用户不需要源码安装，直接使用上面的插件安装方式即可。

只有在你想检查代码、修改代码、或手动运行脚本时，才需要 clone 源码：

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

这个仓库是一个公开的 Codex plugin marketplace source。OpenAI-curated 公共插件目录目前不是自助上架流程，所以用户通过添加这个 GitHub 仓库作为 marketplace source 来安装插件。

## 许可证

MIT
