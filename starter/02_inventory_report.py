#!/usr/bin/env python3
"""Collect a lightweight hardware/software inventory report."""
import argparse
from netops_kit.cli import inventory_arg, run_mapped_command

p = argparse.ArgumentParser(description=__doc__)
inventory_arg(p)
a = p.parse_args()
run_mapped_command(a.inventory, "facts", a.workers, a.output, "facts")
