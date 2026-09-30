#!/usr/bin/env python3
"""Fast TCP reachability check for the management port of each device."""
import argparse
from netops_kit.core import load_inventory, tcp_reachable

p = argparse.ArgumentParser(description=__doc__)
p.add_argument("-i", "--inventory", default="examples/inventory.yml")
p.add_argument("--timeout", type=float, default=2.0)
a = p.parse_args()

failed = 0
for device in load_inventory(a.inventory):
    port = int(device.get("port", 22))
    ok, detail = tcp_reachable(device["host"], port, a.timeout)
    print(f"[{'OK' if ok else 'DOWN'}] {device['name']} {device['host']}:{port} - {detail}")
    failed += 0 if ok else 1
raise SystemExit(1 if failed else 0)
