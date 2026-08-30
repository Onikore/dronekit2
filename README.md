# dronekit2

![dronekit_python_logo](https://cloud.githubusercontent.com/assets/5368500/10805537/90dd4b14-7e22-11e5-9592-5925348a7df9.png)

[![CI](https://github.com/Onikore/dronekit2/actions/workflows/ci.yml/badge.svg)](https://github.com/Onikore/dronekit2/actions/workflows/ci.yml)

**dronekit2** is a maintained fork of [DroneKit-Python](https://github.com/dronekit/dronekit-python),
which has had no release since 2019 and does not import on modern Python. This fork keeps the
`dronekit` import path and the attribute/observer API developers already know, modernizes the
packaging and internals, and fixes real defects found along the way. See
[`CHANGELOG.md`](CHANGELOG.md) and [`docs/about/migrating_v3.rst`](docs/about/migrating_v3.rst)
for exactly what changed from the 2.9.x line.

DroneKit-Python helps you create apps for UAVs. It provides programmatic access to a connected
vehicle's telemetry, state and parameter information over MAVLink, and supports both mission
management and direct control over vehicle movement.

## Installing

Requires Python 3.9+.

```bash
pip install dronekit2
```

Import name is unchanged:

```python
import dronekit
```

To track `main` instead of the latest release, install straight from this repo:

```bash
pip install git+https://github.com/Onikore/dronekit2.git
```

## Getting started

```python
from dronekit import connect

# Connect to a vehicle (real or simulated) speaking MAVLink on this UDP endpoint.
vehicle = connect("127.0.0.1:14550", wait_ready=True)

# Use the returned Vehicle object to query device state - e.g. to get the mode:
print(f"Mode: {vehicle.mode.name}")

vehicle.close()
```

See [`docs/guide/quick_start.rst`](docs/guide/quick_start.rst) for a full walkthrough (including
how to run this against ArduPilot SITL), [`docs/guide/`](docs/guide/) for the rest of the guide,
and [`examples/`](examples/) for runnable end-to-end scripts.

## Documentation

Full docs are hosted at **[onikore.github.io/dronekit2](https://onikore.github.io/dronekit2/)**
(built from [`docs/`](docs/) on every push to `main`). You can also browse the reStructuredText
source on GitHub, or build it locally:

```bash
pip install -e ".[docs]"
sphinx-build -b html docs docs/_build/html
```

* [Guide](https://onikore.github.io/dronekit2/guide/index.html)
* [API reference](https://onikore.github.io/dronekit2/automodule.html)
* [Examples](https://onikore.github.io/dronekit2/examples/index.html)
* [Migrating from 2.9.x](https://onikore.github.io/dronekit2/about/migrating_v3.html)

## Testing against a real vehicle

The test suite skips anything that needs a live vehicle unless `DRONEKIT_TEST_CONNECTION` is set
— it accepts either an ArduPilot SITL connection string or a real flight controller over serial.
See [`dronekit/test/README.md`](dronekit/test/README.md).

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for development setup, and the
[Code of Conduct](CODE_OF_CONDUCT.md) before participating.

Questions and bug reports: [open an issue](https://github.com/Onikore/dronekit2/issues). Security
vulnerabilities: see [`SECURITY.md`](SECURITY.md) rather than filing a public issue.

## Licence

dronekit2 is made available under the [Apache 2.0 License](LICENSE).

***

Copyright 2015 3D Robotics, Inc. Portions Copyright 2026 the dronekit2 contributors.
