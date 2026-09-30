#!/usr/bin/env python3
"""Back up running configurations from all inventory devices."""
import argparse
from netops_kit.cli import inventory_arg, run_mapped_command

p = argparse.ArgumentParser(description=__doc__)
inventory_arg(p)
a = p.parse_args()
run_mapped_command(a.inventory, "running_config", a.workers, a.output, "running_config")
