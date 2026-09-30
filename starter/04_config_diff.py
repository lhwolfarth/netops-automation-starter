#!/usr/bin/env python3
"""Compare live running config with a saved baseline directory."""
import argparse
from pathlib import Path
from netops_kit.commands import get_command
from netops_kit.core import load_inventory, run_command, unified_diff, safe_name

p = argparse.ArgumentParser(description=__doc__)
p.add_argument("-i", "--inventory", default="examples/inventory.yml")
p.add_argument("-b", "--baseline", default="examples/configs", help="Directory containing <device>.cfg baselines")
a = p.parse_args()

for device in load_inventory(a.inventory):
    baseline = Path(a.baseline) / f"{safe_name(device['name'])}.cfg"
    if not baseline.exists():
        print(f"[SKIP] {device['name']}: no baseline {baseline}")
        continue
    result = run_command(device, get_command(device, "running_config"))
    if not result.ok:
        print(f"[ERROR] {device['name']}: {result.output}")
        continue
    diff = unified_diff(baseline.read_text(encoding="utf-8"), result.output, str(baseline), f"{device['name']}:live")
    print(f"\n### {device['name']}\n{diff or 'No differences.'}")
