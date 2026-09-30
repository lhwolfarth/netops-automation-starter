from pathlib import Path

import pytest

from netops_kit.core import (
    connection_params,
    load_inventory,
    parse_bool,
    safe_name,
    unified_diff,
    validate_operational_command,
)


def test_inventory_merge(tmp_path: Path):
    p = tmp_path / "inv.yml"
    p.write_text(
        """
defaults:
  port: 22
devices:
  - name: r1
    host: 192.0.2.1
""",
        encoding="utf-8",
    )
    devices = load_inventory(p)
    assert devices[0]["name"] == "r1"
    assert devices[0]["port"] == 22


def test_inventory_rejects_empty(tmp_path: Path):
    p = tmp_path / "inv.yml"
    p.write_text("devices: []\n", encoding="utf-8")
    with pytest.raises(ValueError, match="no devices"):
        load_inventory(p)


def test_unified_diff_detects_change():
    diff = unified_diff("hostname r1\n", "hostname r2\n")
    assert "-hostname r1" in diff
    assert "+hostname r2" in diff


@pytest.mark.parametrize(
    ("value", "expected"),
    [(True, True), (False, False), ("true", True), ("FALSE", False), ("yes", True), ("0", False), (1, True)],
)
def test_parse_bool(value, expected):
    assert parse_bool(value) is expected


def test_safe_name():
    assert safe_name("core/sw 01") == "core_sw_01"


def test_operational_command_guard():
    assert validate_operational_command("show ip route") == "show ip route"
    assert validate_operational_command("display interface brief") == "display interface brief"
    with pytest.raises(ValueError):
        validate_operational_command("reload")
    with pytest.raises(ValueError):
        validate_operational_command("configure terminal")


def test_operational_command_unsafe_escape_hatch():
    assert validate_operational_command("request system reboot", allow_unsafe=True) == "request system reboot"


def test_connection_params_from_env(monkeypatch):
    monkeypatch.setenv("NETOPS_USERNAME", "alice")
    monkeypatch.setenv("NETOPS_PASSWORD", "secret")
    params = connection_params({"name": "r1", "host": "192.0.2.1", "fast_cli": "false"})
    assert params["username"] == "alice"
    assert params["password"] == "secret"
    assert params["fast_cli"] is False
