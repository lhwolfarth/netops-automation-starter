from __future__ import annotations

import argparse
from pathlib import Path

from .core import DeviceResult, load_inventory, parallel, run_command, save_text, ensure_output_dir
from .commands import get_command


def inventory_arg(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("-i", "--inventory", default="examples/inventory.yml", help="Inventory YAML path")
    parser.add_argument("-w", "--workers", type=int, default=10, help="Parallel workers")
    parser.add_argument("-o", "--output", default="output", help="Output directory")


def run_mapped_command(inventory: str, command_key: str, workers: int, output: str, suffix: str | None = None) -> list[DeviceResult]:
    devices = load_inventory(inventory)
    outdir = ensure_output_dir(output)

    def worker(device: dict) -> DeviceResult:
        try:
            command = get_command(device, command_key)
        except Exception as exc:  # noqa: BLE001
            return DeviceResult(device["name"], False, str(exc), 0.0)
        return run_command(device, command)

    results = parallel(devices, worker, workers)
    for result in sorted(results, key=lambda r: r.device):
        label = "OK" if result.ok else "ERROR"
        print(f"[{label}] {result.device} ({result.elapsed_s:.2f}s)")
        save_text(outdir, result.device, suffix or command_key, result.output)
    print(f"Saved results to {Path(outdir).resolve()}")
    return results
