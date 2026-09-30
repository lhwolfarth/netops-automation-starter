# 3-minute demo

This demo is designed for a terminal recording without showing a presenter on camera.

## Scene 1 — the repetitive problem

Show an inventory with three lab devices, then run:

```bash
python starter/05_reachability_check.py -i inventory.yml
```

Explain: before touching a fleet, verify the management plane.

## Scene 2 — backup

```bash
python starter/01_backup_configs.py -i inventory.yml
```

Open the timestamped output directory and show the per-device files.

## Scene 3 — drift

Keep a known baseline in `examples/configs/`, make one harmless lab-only hostname/description change, then run:

```bash
python starter/04_config_diff.py -i inventory.yml --baseline examples/configs
```

Zoom in on the unified diff.

## Closing line

"Five free workflows. No cloud dependency. Keep the code, adapt it to your network, and test everything in a lab first."
