# Contributing to dronekit2

Please see the [Contributing guide](docs/contributing/index.rst) in `docs/` for the full
picture (reporting issues, contributing to the API vs. docs, per-OS dev environment setup).

## Development setup

```bash
git clone https://github.com/Onikore/dronekit2.git
cd dronekit2
pip install -e ".[dev]"
pytest dronekit/test
pre-commit install
```

* `pip install -e ".[dev]"` installs the package in editable mode plus `pytest`, `ruff`, and
  `mypy`.
* `pytest dronekit/test` runs the test suite. Tests that need a live vehicle/SITL connection are
  skipped automatically unless the `DRONEKIT_TEST_CONNECTION` environment variable is set (e.g.
  `DRONEKIT_TEST_CONNECTION=udp:127.0.0.1:14550` for SITL, or a serial device for real hardware).
* `pre-commit install` wires up the hooks in `.pre-commit-config.yaml` (ruff lint/format plus a
  few basic file hygiene checks) to run on `git commit`.

Please read the [Code of Conduct](CODE_OF_CONDUCT.md) before participating.
