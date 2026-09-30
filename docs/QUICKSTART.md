# Quick Start

## 1. Requirements

- Python 3.10+
- SSH access to lab/network devices
- NETCONF enabled only for the NETCONF modules

## 2. Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
```

## 3. Configure credentials

Linux/macOS:

```bash
export NETOPS_USERNAME='automation'
export NETOPS_PASSWORD='your-password'
export NETOPS_SECRET='your-enable-secret'
```

PowerShell:

```powershell
$env:NETOPS_USERNAME='automation'
$env:NETOPS_PASSWORD='your-password'
$env:NETOPS_SECRET='your-enable-secret'
```

Do not commit secrets to Git.

## 4. Build your inventory

Copy `examples/inventory.yml` and replace the RFC 5737 example addresses with lab addresses.

`device_type` is the Netmiko driver. `platform` selects the built-in command map. A device can override any mapped command:

```yaml
- name: custom-switch
  host: 10.10.10.10
  device_type: cisco_ios
  platform: cisco_ios
  commands:
    interfaces: show interfaces brief
```

## 5. Verify reachability

```bash
python starter/05_reachability_check.py -i inventory.yml
```

## 6. Back up configurations

```bash
python starter/01_backup_configs.py -i inventory.yml
```

Outputs are stored under timestamped directories beneath `output/`.

## 7. Next steps

Read `docs/ROADMAP.md`, adapt the example inventory, and validate command output against your lab devices before production use.
