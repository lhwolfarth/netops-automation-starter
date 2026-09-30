from __future__ import annotations

import concurrent.futures
import difflib
import json
import os
import re
import socket
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable

import yaml


@dataclass
class DeviceResult:
    device: str
    ok: bool
    output: str
    elapsed_s: float


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def parse_bool(value: Any, *, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value != 0
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"1", "true", "yes", "on"}:
            return True
        if normalized in {"0", "false", "no", "off", ""}:
            return False
    raise ValueError(f"Cannot interpret {value!r} as a boolean.")


def load_inventory(path: str | Path) -> list[dict[str, Any]]:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError("Inventory root must be a YAML mapping.")
    defaults = data.get("defaults", {}) or {}
    if not isinstance(defaults, dict):
        raise ValueError("Inventory 'defaults' must be a mapping.")
    devices = []
    for item in data.get("devices", []) or []:
        if not isinstance(item, dict):
            raise ValueError("Every device entry must be a mapping.")
        merged = {**defaults, **item}
        if "name" not in merged or "host" not in merged:
            raise ValueError("Every device requires 'name' and 'host'.")
        devices.append(merged)
    if not devices:
        raise ValueError("Inventory contains no devices.")
    return devices


def env_or_value(value: Any) -> Any:
    if isinstance(value, str) and value.startswith("env:"):
        key = value.split(":", 1)[1]
        return os.getenv(key)
    return value


def credentials(device: dict[str, Any]) -> tuple[str, str, str | None]:
    username = env_or_value(device.get("username")) or os.getenv("NETOPS_USERNAME")
    password = env_or_value(device.get("password")) or os.getenv("NETOPS_PASSWORD")
    secret = env_or_value(device.get("secret")) or os.getenv("NETOPS_SECRET")
    if not username or not password:
        raise ValueError(
            f"Missing credentials for {device['name']}. Set NETOPS_USERNAME/NETOPS_PASSWORD "
            "or use env:VARIABLE references in inventory.yml."
        )
    return str(username), str(password), str(secret) if secret else None


def connection_params(device: dict[str, Any]) -> dict[str, Any]:
    username, password, secret = credentials(device)
    params: dict[str, Any] = {
        "device_type": device.get("device_type", "cisco_ios"),
        "host": device["host"],
        "username": username,
        "password": password,
        "port": int(device.get("port", 22)),
        "timeout": int(device.get("timeout", 15)),
        "conn_timeout": int(device.get("conn_timeout", 10)),
        "fast_cli": parse_bool(device.get("fast_cli"), default=True),
        "ssh_strict": parse_bool(device.get("ssh_strict"), default=False),
    }
    if secret:
        params["secret"] = secret
    return params


def run_command(device: dict[str, Any], command: str) -> DeviceResult:
    started = time.monotonic()
    try:
        try:
            from netmiko import ConnectHandler
        except ImportError as exc:
            raise RuntimeError("Netmiko is required. Install with: pip install -e .") from exc
        with ConnectHandler(**connection_params(device)) as conn:
            if parse_bool(device.get("enable"), default=False) and (device.get("secret") or os.getenv("NETOPS_SECRET")):
                conn.enable()
            output = conn.send_command(command, read_timeout=int(device.get("read_timeout", 60)))
        return DeviceResult(device["name"], True, output, time.monotonic() - started)
    except Exception as exc:  # noqa: BLE001
        return DeviceResult(device["name"], False, f"{type(exc).__name__}: {exc}", time.monotonic() - started)


def send_config(device: dict[str, Any], commands: list[str], *, apply: bool = False) -> DeviceResult:
    started = time.monotonic()
    if not commands:
        return DeviceResult(device["name"], False, "No configuration commands supplied.", time.monotonic() - started)
    if not apply:
        preview = "\n".join(commands)
        return DeviceResult(device["name"], True, f"DRY-RUN\n{preview}", time.monotonic() - started)
    try:
        try:
            from netmiko import ConnectHandler
        except ImportError as exc:
            raise RuntimeError("Netmiko is required. Install with: pip install -e .") from exc
        with ConnectHandler(**connection_params(device)) as conn:
            if parse_bool(device.get("enable"), default=False) and (device.get("secret") or os.getenv("NETOPS_SECRET")):
                conn.enable()
            output = conn.send_config_set(commands)
        return DeviceResult(device["name"], True, output, time.monotonic() - started)
    except Exception as exc:  # noqa: BLE001
        return DeviceResult(device["name"], False, f"{type(exc).__name__}: {exc}", time.monotonic() - started)


def validate_operational_command(command: str, *, allow_unsafe: bool = False) -> str:
    cmd = command.strip()
    if not cmd:
        raise ValueError("Command cannot be empty.")
    if "\n" in cmd or "\r" in cmd:
        raise ValueError("Only one operational command may be supplied at a time.")
    if allow_unsafe:
        return cmd
    if not re.match(r"^(show|display)\s+", cmd, flags=re.IGNORECASE):
        raise ValueError(
            "Generic runner accepts only commands beginning with 'show' or 'display'. "
            "Use --unsafe-exec only after reviewing the command and device behavior."
        )
    return cmd


def parallel(
    devices: Iterable[dict[str, Any]],
    worker: Callable[[dict[str, Any]], DeviceResult],
    max_workers: int = 10,
) -> list[DeviceResult]:
    device_list = list(devices)
    if not device_list:
        return []
    if max_workers < 1:
        raise ValueError("max_workers must be >= 1")
    max_workers = min(max_workers, 100)
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = [pool.submit(worker, d) for d in device_list]
        return [f.result() for f in concurrent.futures.as_completed(futures)]


def ensure_output_dir(base: str | Path = "output") -> Path:
    path = Path(base) / utc_stamp()
    path.mkdir(parents=True, exist_ok=True)
    return path


def safe_name(name: str) -> str:
    return "".join(ch if ch.isalnum() or ch in "-_." else "_" for ch in name)


def save_text(outdir: Path, device: str, suffix: str, content: str) -> Path:
    path = outdir / f"{safe_name(device)}_{suffix}.txt"
    path.write_text(content, encoding="utf-8")
    return path


def save_json(outdir: Path, filename: str, payload: Any) -> Path:
    path = outdir / filename
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def unified_diff(old: str, new: str, fromfile: str = "saved", tofile: str = "live") -> str:
    return "".join(
        difflib.unified_diff(
            old.splitlines(keepends=True),
            new.splitlines(keepends=True),
            fromfile=fromfile,
            tofile=tofile,
        )
    )


def tcp_reachable(host: str, port: int = 22, timeout: float = 2.0) -> tuple[bool, str]:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True, "reachable"
    except OSError as exc:
        return False, str(exc)
