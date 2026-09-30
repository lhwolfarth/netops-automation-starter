# Contributing

Contributions that improve safety, portability, tests, documentation, or vendor command mappings are welcome.

1. Test changes against lab equipment or a simulator whenever possible.
2. Never commit credentials or real customer configurations.
3. Keep state-changing behavior opt-in and obvious.
4. Add or update tests for shared-library changes.
5. Describe the vendor, platform, and software release used for validation.

Run before submitting:

```bash
pip install -e ".[dev]"
ruff check .
pytest -q
python -m compileall -q netops_kit starter
```
