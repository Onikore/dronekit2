# dronekit-python tests

Tests are run with pytest:

```
$ python -m pytest dronekit/test
```

## Unit tests

`dronekit/test/unit` needs no connection at all and always runs.

## Live-vehicle tests

`dronekit/test/sitl` needs a live vehicle to talk to over MAVLink - either a
running ArduPilot SITL instance, or a real flight controller connected over
serial/USB. Point the `DRONEKIT_TEST_CONNECTION` environment variable at
whatever `dronekit.connect()` should use, e.g.:

```
export DRONEKIT_TEST_CONNECTION=tcp:127.0.0.1:5760   # SITL over TCP
export DRONEKIT_TEST_CONNECTION=udp:127.0.0.1:14550  # SITL/companion link over UDP
export DRONEKIT_TEST_CONNECTION=com3                 # real flight controller (Windows)
export DRONEKIT_TEST_CONNECTION=/dev/ttyACM0         # real flight controller (Linux)
```

If `DRONEKIT_TEST_CONNECTION` is not set, these tests are skipped rather than
failed - nothing here starts a simulator on your behalf.

These tests are also marked `sitl` (see `dronekit/test/conftest.py`), so they
can be selected or excluded explicitly:

```
$ python -m pytest dronekit/test -m sitl        # only the live-vehicle tests
$ python -m pytest dronekit/test -m "not sitl"   # everything except those
```
