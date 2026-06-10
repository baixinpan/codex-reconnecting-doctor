#!/usr/bin/env python3
"""Diagnose and repair Codex Desktop reconnect loops caused by proxy or WSS issues."""

from __future__ import annotations

import argparse
import json
import os
import platform
import re
import shutil
import socket
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable


PROXY_KEYS = ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy")
PROXY_PROCESS_RE = re.compile(
    r"(clash|verge|mihomo|surge|sing-box|singbox|v2ray|xray|loon|proxy)",
    re.IGNORECASE,
)
COMMON_PROXY_PORTS = (7897, 7890, 7899, 7891, 1080, 1087, 20170, 6152)
DEFAULT_TEST_URL = "https://api.openai.com"


@dataclass
class ProxyCandidate:
    host: str
    port: int
    source: str
    process: str = ""
    connect_ok: bool = False
    curl_summary: str = ""
    score: int = 0
    tcp_open: bool = False

    @property
    def url(self) -> str:
        return f"http://{self.host}:{self.port}"


def run(cmd: list[str], timeout: int = 10) -> tuple[int, str]:
    try:
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=timeout,
            check=False,
        )
        return proc.returncode, proc.stdout
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        return 127, str(exc)


def codex_home() -> Path:
    return Path(os.environ.get("CODEX_HOME", "~/.codex")).expanduser()


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def redact(value: str, include_private: bool) -> str:
    if include_private:
        return value
    value = re.sub(r"(?i)(api[_-]?key|token|authorization|bearer)\s*[:=]\s*[^\s,;]+", r"\1=<redacted>", value)
    value = re.sub(r"(?i)(https?://)([^/@\s]+):([^/@\s]+)@", r"\1<redacted>:<redacted>@", value)
    value = re.sub(r"(?i)([?&](?:key|token|api_key|access_token)=)[^&\s]+", r"\1<redacted>", value)
    return value


def parse_proxy_url(value: str, source: str) -> ProxyCandidate | None:
    value = value.strip().strip('"').strip("'")
    match = re.search(r"(?:(?:https?|socks5?)://)?([^:/\s]+):(\d{2,5})", value)
    if not match:
        return None
    host = match.group(1)
    try:
        port = int(match.group(2))
    except ValueError:
        return None
    if not (1 <= port <= 65535):
        return None
    return ProxyCandidate(host=host, port=port, source=source)


def env_candidates(env_path: Path) -> list[ProxyCandidate]:
    out: list[ProxyCandidate] = []
    for key, value in os.environ.items():
        if key.lower() in {"http_proxy", "https_proxy", "all_proxy"}:
            candidate = parse_proxy_url(value, f"process env {key}")
            if candidate:
                out.append(candidate)
    for line in read_text(env_path).splitlines():
        match = re.match(r"\s*(HTTP_PROXY|HTTPS_PROXY|http_proxy|https_proxy)\s*=\s*(.+?)\s*$", line)
        if match:
            candidate = parse_proxy_url(match.group(2), f"{env_path} {match.group(1)}")
            if candidate:
                out.append(candidate)
    return out


def windows_env_proxy_candidates() -> list[ProxyCandidate]:
    out: list[ProxyCandidate] = []
    for key in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy"):
        value = os.environ.get(key)
        if value:
            candidate = parse_proxy_url(value, f"environment {key}")
            if candidate:
                out.append(candidate)
    return out


def macos_system_proxy_candidates() -> list[ProxyCandidate]:
    if platform.system() != "Darwin":
        return []
    code, output = run(["scutil", "--proxy"])
    if code != 0:
        return []
    host = "127.0.0.1"
    http_enabled = re.search(r"HTTPEnable\s*:\s*1", output)
    https_enabled = re.search(r"HTTPSEnable\s*:\s*1", output)
    http_port = re.search(r"HTTPPort\s*:\s*(\d+)", output)
    https_port = re.search(r"HTTPSPort\s*:\s*(\d+)", output)
    http_proxy = re.search(r"HTTPProxy\s*:\s*(\S+)", output)
    https_proxy = re.search(r"HTTPSProxy\s*:\s*(\S+)", output)
    out: list[ProxyCandidate] = []
    if http_enabled and http_port:
        out.append(
            ProxyCandidate(
                host=http_proxy.group(1) if http_proxy else host,
                port=int(http_port.group(1)),
                source="macOS system HTTP proxy",
            )
        )
    if https_enabled and https_port:
        out.append(
            ProxyCandidate(
                host=https_proxy.group(1) if https_proxy else host,
                port=int(https_port.group(1)),
                source="macOS system HTTPS proxy",
            )
        )
    return out


def listener_candidates() -> list[ProxyCandidate]:
    commands = [
        ["lsof", "-nP", "-iTCP", "-sTCP:LISTEN"],
        ["ss", "-ltnp"],
        ["netstat", "-anv", "-p", "tcp"],
    ]
    out: list[ProxyCandidate] = []
    for cmd in commands:
        code, output = run(cmd)
        if code != 0:
            continue
        for line in output.splitlines():
            lowered = line.lower()
            if not (PROXY_PROCESS_RE.search(line) or any(f":{p}" in lowered or f".{p}" in lowered for p in COMMON_PROXY_PORTS)):
                continue
            for match in re.finditer(r"(?:127\.0\.0\.1|localhost|0\.0\.0\.0|\*)[.:](\d{2,5})", line):
                port = int(match.group(1))
                if 1 <= port <= 65535:
                    source = f"listener via {cmd[0]}"
                    out.append(ProxyCandidate(host="127.0.0.1", port=port, source=source, process=line.strip()))
        if out:
            break
    return out


def common_port_candidates(host: str = "127.0.0.1") -> list[ProxyCandidate]:
    out: list[ProxyCandidate] = []
    for port in COMMON_PROXY_PORTS:
        out.append(ProxyCandidate(host=host, port=port, source="common local proxy port"))
    return out


def socket_open(host: str, port: int) -> bool:
    try:
        with socket.create_connection((host, port), timeout=2):
            return True
    except OSError:
        return False


def verify_http_connect(candidate: ProxyCandidate, test_url: str) -> ProxyCandidate:
    if not socket_open(candidate.host, candidate.port):
        candidate.curl_summary = "TCP connection failed"
        return candidate
    candidate.tcp_open = True
    if not shutil.which("curl"):
        candidate.connect_ok = True
        candidate.curl_summary = "TCP open; curl unavailable for HTTP CONNECT verification"
        candidate.score += 1
        return candidate
    code, output = run(
        ["curl", "-sS", "-I", "--max-time", "12", "-x", candidate.url, test_url],
        timeout=15,
    )
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    candidate.curl_summary = " | ".join(lines[:5]) if lines else f"curl exit {code}"
    if "200 Connection established" in output:
        candidate.connect_ok = True
        candidate.score += 100
    elif code == 0 and re.search(r"HTTP/[0-9.]+\s+(401|403|404|421)", output):
        candidate.score += 10
    return candidate


def dedupe(candidates: Iterable[ProxyCandidate]) -> list[ProxyCandidate]:
    seen: dict[tuple[str, int], ProxyCandidate] = {}
    for candidate in candidates:
        key = (candidate.host, candidate.port)
        existing = seen.get(key)
        if existing:
            existing.source = f"{existing.source}; {candidate.source}"
            if candidate.process and not existing.process:
                existing.process = candidate.process
        else:
            seen[key] = candidate
    return list(seen.values())


def choose_proxy(candidates: list[ProxyCandidate]) -> ProxyCandidate | None:
    verified = [c for c in candidates if c.connect_ok]
    if not verified:
        return None
    for candidate in verified:
        if PROXY_PROCESS_RE.search(candidate.process):
            candidate.score += 20
        if "codex/.env" in candidate.source:
            candidate.score += 5
        if candidate.port in COMMON_PROXY_PORTS:
            candidate.score += 3
    return sorted(verified, key=lambda c: (c.score, -c.port), reverse=True)[0]


def parse_active_provider(config_path: Path) -> tuple[str | None, str | None, bool | None]:
    text = read_text(config_path)
    provider_match = re.search(r'(?m)^\s*model_provider\s*=\s*"([^"]+)"', text)
    provider = provider_match.group(1) if provider_match else None
    if not provider:
        return None, None, None
    block_re = re.compile(
        rf'(?ms)^\[model_providers\.{re.escape(provider)}\]\s*(.*?)(?=^\[|\Z)'
    )
    block_match = block_re.search(text)
    if not block_match:
        return provider, None, None
    block = block_match.group(1)
    base_match = re.search(r'(?m)^\s*base_url\s*=\s*"([^"]+)"', block)
    ws_match = re.search(r"(?m)^\s*supports_websockets\s*=\s*(true|false)", block)
    return (
        provider,
        base_match.group(1) if base_match else None,
        None if not ws_match else ws_match.group(1) == "true",
    )


def provider_probe_url(base_url: str | None) -> str:
    if not base_url:
        return DEFAULT_TEST_URL
    base = base_url.rstrip("/")
    if re.search(r"/v1(?:/|$)", base):
        return base + "/models"
    return base


def test_direct_url(url: str) -> str:
    if not shutil.which("curl"):
        return "curl unavailable"
    _, output = run(["curl", "-sS", "-I", "--max-time", "12", url], timeout=15)
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    return " | ".join(lines[:5]) if lines else "no response"


def backup(path: Path) -> Path:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_path = path.with_name(f"{path.name}.bak-{stamp}")
    shutil.copy2(path, backup_path)
    return backup_path


def update_env(env_path: Path, proxy_url: str, dry_run: bool) -> tuple[bool, str]:
    original = read_text(env_path)
    lines = original.splitlines()
    seen = set()
    changed = False
    new_lines: list[str] = []
    for line in lines:
        match = re.match(r"\s*(HTTP_PROXY|HTTPS_PROXY|http_proxy|https_proxy)\s*=", line)
        if match:
            key = match.group(1)
            seen.add(key)
            replacement = f'{key}="{proxy_url}"'
            new_lines.append(replacement)
            changed = changed or replacement != line
        else:
            new_lines.append(line)
    for key in PROXY_KEYS:
        if key not in seen:
            new_lines.append(f'{key}="{proxy_url}"')
            changed = True
    new_text = "\n".join(new_lines).rstrip() + "\n"
    if not changed:
        return False, "already up to date"
    if dry_run:
        return True, "would update proxy entries"
    if env_path.exists():
        backup_path = backup(env_path)
        note = f"updated; backup {backup_path}"
    else:
        env_path.parent.mkdir(parents=True, exist_ok=True)
        note = "created"
    env_path.write_text(new_text, encoding="utf-8")
    return True, note


def disable_websockets(config_path: Path, dry_run: bool) -> tuple[bool, str]:
    text = read_text(config_path)
    provider, _, ws = parse_active_provider(config_path)
    if not provider:
        return False, "no top-level model_provider found"
    block_re = re.compile(
        rf'(?ms)^(\[model_providers\.{re.escape(provider)}\]\s*)(.*?)(?=^\[|\Z)'
    )
    match = block_re.search(text)
    if not match:
        return False, f"active provider block not found: {provider}"
    block = match.group(2)
    if ws is False:
        return False, "already disabled for active provider"
    if re.search(r"(?m)^\s*supports_websockets\s*=", block):
        new_block = re.sub(
            r"(?m)^(\s*supports_websockets\s*=\s*)(true|false)",
            r"\1false",
            block,
            count=1,
        )
    else:
        insert = 'supports_websockets = false\n'
        wire_match = re.search(r'(?m)^.*wire_api\s*=\s*"responses".*\n?', block)
        if wire_match:
            pos = wire_match.end()
            new_block = block[:pos] + insert + block[pos:]
        else:
            new_block = 'wire_api = "responses"\n' + insert + block
    new_text = text[: match.start(2)] + new_block + text[match.end(2) :]
    if new_text == text:
        return False, "no change needed"
    if dry_run:
        return True, f"would set supports_websockets=false in provider {provider}"
    backup_path = backup(config_path)
    config_path.write_text(new_text, encoding="utf-8")
    return True, f"updated provider {provider}; backup {backup_path}"


def build_report(codex: Path, env_path: Path, config_path: Path, candidates: list[ProxyCandidate], chosen: ProxyCandidate | None, include_private: bool) -> dict:
    provider, base_url, ws = parse_active_provider(config_path)
    probe_url = provider_probe_url(base_url)
    direct_summary = test_direct_url(probe_url)
    health = "ok" if chosen else "needs_proxy"
    if chosen and ws is not False:
        health = "proxy_ok_websocket_unset"
    report = {
        "health": health,
        "platform": f"{platform.system()} {platform.release()}",
        "codex_home": str(codex),
        "env_file": {"path": str(env_path), "exists": env_path.exists()},
        "config_file": {"path": str(config_path), "exists": config_path.exists()},
        "provider": {
            "active_provider": provider,
            "base_url": redact(base_url or "", include_private) or None,
            "supports_websockets": ws,
            "probe_url": redact(probe_url, include_private),
            "direct_probe": redact(direct_summary, include_private),
        },
        "proxy_candidates": [
            {
                "url": redact(candidate.url, include_private),
                "source": redact(candidate.source, include_private),
                "process": redact(candidate.process[:240], include_private),
                "tcp_open": candidate.tcp_open,
                "connect_ok": candidate.connect_ok,
                "verify": redact(candidate.curl_summary[:300], include_private),
                "score": candidate.score,
            }
            for candidate in candidates
        ],
        "chosen_proxy": None if not chosen else redact(chosen.url, include_private),
        "recommendations": [],
    }
    if chosen:
        report["recommendations"].append(f"use proxy {redact(chosen.url, include_private)}")
        report["recommendations"].append("run --fix-env when ~/.codex/.env is missing, stale, or inconsistent")
    else:
        report["recommendations"].append("start or fix the local proxy client; no verified HTTP/mixed proxy was found")
    if ws is not False:
        report["recommendations"].append("run --disable-websockets if reconnecting continues after proxy repair")
    report["recommendations"].append("restart Codex Desktop after config changes")
    return report


def print_report(report: dict) -> None:
    print("Codex reconnect doctor")
    print("=" * 24)
    print(f"health: {report['health']}")
    print(f"platform: {report['platform']}")
    print(f"codex_home: {report['codex_home']}")
    print(f"env_file: {report['env_file']['path']} ({'exists' if report['env_file']['exists'] else 'missing'})")
    print(f"config_file: {report['config_file']['path']} ({'exists' if report['config_file']['exists'] else 'missing'})")
    print()
    print("Provider")
    print("-" * 8)
    provider = report["provider"]
    ws = provider["supports_websockets"]
    print(f"active_provider: {provider['active_provider'] or 'unknown'}")
    print(f"base_url: {provider['base_url'] or 'unknown'}")
    print(f"supports_websockets: {'unset' if ws is None else str(ws).lower()}")
    print(f"probe_url: {provider['probe_url']}")
    print(f"direct_probe: {provider['direct_probe']}")
    print()
    print("Proxy candidates")
    print("-" * 16)
    if not report["proxy_candidates"]:
        print("none found")
    for candidate in report["proxy_candidates"]:
        status = "CONNECT_OK" if candidate["connect_ok"] else ("TCP_ONLY" if candidate["tcp_open"] else "not_verified")
        print(f"{status} {candidate['url']} source={candidate['source']}")
        if candidate["process"]:
            print(f"  process: {candidate['process'][:180]}")
        if candidate["verify"]:
            print(f"  verify: {candidate['verify'][:220]}")
    print()
    print("Recommendation")
    print("-" * 14)
    for item in report["recommendations"]:
        print(item)


def main() -> int:
    parser = argparse.ArgumentParser(description="Diagnose and repair Codex Desktop reconnect loops.")
    parser.add_argument("--codex-home", type=Path, default=codex_home(), help="Codex home directory; default: CODEX_HOME or ~/.codex")
    parser.add_argument("--test-url", default=DEFAULT_TEST_URL, help="URL used for HTTP CONNECT verification")
    parser.add_argument("--proxy-port", type=int, help="Manually specify a local HTTP/mixed proxy port")
    parser.add_argument("--proxy-host", default="127.0.0.1", help="Proxy host for --proxy-port")
    parser.add_argument("--no-common-ports", action="store_true", help="Skip probing common local proxy ports")
    parser.add_argument("--json", action="store_true", help="Print a JSON report for issue templates or automation")
    parser.add_argument("--include-private", action="store_true", help="Do not redact URLs/process lines in reports")
    parser.add_argument("--fix-env", action="store_true", help="Update ~/.codex/.env with the verified HTTP/mixed proxy")
    parser.add_argument("--disable-websockets", action="store_true", help="Set supports_websockets=false in the active provider block")
    parser.add_argument("--dry-run", action="store_true", help="Show what would change without writing files")
    args = parser.parse_args()

    codex = args.codex_home.expanduser()
    env_path = codex / ".env"
    config_path = codex / "config.toml"

    candidates = []
    if args.proxy_port:
        candidates.append(ProxyCandidate(args.proxy_host, args.proxy_port, "manual --proxy-port"))
    candidates.extend(env_candidates(env_path))
    candidates.extend(windows_env_proxy_candidates())
    candidates.extend(macos_system_proxy_candidates())
    candidates.extend(listener_candidates())
    if not args.no_common_ports:
        candidates.extend(common_port_candidates())
    candidates = dedupe(candidates)
    for candidate in candidates:
        verify_http_connect(candidate, args.test_url)
    chosen = choose_proxy(candidates)

    report = build_report(codex, env_path, config_path, candidates, chosen, args.include_private)
    report["actions"] = []
    if not args.json:
        print_report(report)

    if args.fix_env:
        if not chosen:
            note = "skipped: no verified HTTP/mixed proxy"
            report["actions"].append({"name": "fix_env", "changed": False, "note": note})
            if not args.json:
                print()
                print("Env update")
                print("-" * 10)
                print(note)
            return 2
        changed, note = update_env(env_path, chosen.url, args.dry_run)
        report["actions"].append({"name": "fix_env", "changed": changed, "note": note})
        if not args.json:
            print()
            print("Env update")
            print("-" * 10)
            print(("changed: " if changed else "unchanged: ") + note)

    if args.disable_websockets:
        if not config_path.exists():
            note = "skipped: config.toml missing"
            report["actions"].append({"name": "disable_websockets", "changed": False, "note": note})
            if not args.json:
                print()
                print("WebSocket config")
                print("-" * 16)
                print(note)
            return 2
        changed, note = disable_websockets(config_path, args.dry_run)
        report["actions"].append({"name": "disable_websockets", "changed": changed, "note": note})
        if not args.json:
            print()
            print("WebSocket config")
            print("-" * 16)
            print(("changed: " if changed else "unchanged: ") + note)

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
