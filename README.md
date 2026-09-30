# NetOps Automation Starter v0.2

**Five free, lab-first Python workflows for network engineers.**

This repository targets repetitive day-to-day operations: reachability checks, configuration backups, inventory collection, interface status and configuration drift. It is intentionally small, readable and easy to adapt.

> **Safety:** test against lab equipment first. The project does not claim universal device/OS compatibility.

## Included workflows

| # | Workflow | Purpose |
|---|---|---|
| 1 | `01_backup_configs.py` | Save timestamped running-config backups |
| 2 | `02_inventory_report.py` | Collect device facts |
| 3 | `03_interface_status.py` | Collect interface status |
| 4 | `04_config_diff.py` | Compare live config with a saved baseline |
| 5 | `05_reachability_check.py` | Check TCP management-plane reachability |

Built-in command maps cover Cisco IOS, IOS XE, NX-OS, Arista EOS and Juniper Junos. These are **command mappings**, not a blanket compatibility guarantee.

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
export NETOPS_USERNAME='labuser'
export NETOPS_PASSWORD='labpassword'
cp examples/inventory.yml inventory.yml
python starter/05_reachability_check.py -i inventory.yml
python starter/01_backup_configs.py -i inventory.yml
```

Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
$env:NETOPS_USERNAME='labuser'
$env:NETOPS_PASSWORD='labpassword'
```

Read [`docs/QUICKSTART.md`](docs/QUICKSTART.md) before using real devices.

## Safety principles

- Credentials are expected from environment variables.
- No telemetry or mandatory cloud service.
- Read-only workflows are the focus of the free edition.
- Optional strict SSH host-key verification is supported with `ssh_strict: true`.
- Output is stored locally.

## Why this exists

Network engineers often rewrite the same small scripts for every environment. This project provides a clean baseline that can be kept, audited and adapted instead of starting from an empty file every time.

## Want the deeper workflows?

The paid editions extend into compliance, pre/post maintenance validation, Jinja2 rendering, guarded bulk configuration changes, NETCONF and parallel operational collection.

## License

MIT. See `LICENSE.txt`.
