"""Shared pytest fixtures for the dronekit test suite.

Most of the tests under ``dronekit/test/sitl`` need a *live* vehicle to talk
to over MAVLink - either a running ArduPilot SITL instance, or a real flight
controller connected over serial/USB. Point the ``DRONEKIT_TEST_CONNECTION``
environment variable at whatever ``dronekit.connect()`` should use, e.g.:

    DRONEKIT_TEST_CONNECTION=tcp:127.0.0.1:5760   # SITL over TCP
    DRONEKIT_TEST_CONNECTION=udp:127.0.0.1:14550  # SITL/companion link over UDP
    DRONEKIT_TEST_CONNECTION=com3                 # real flight controller (Windows)
    DRONEKIT_TEST_CONNECTION=/dev/ttyACM0         # real flight controller (Linux)

No simulator is started by this file. The package this suite used to rely on
for downloading and launching ArduPilot binaries is dead (its asset host
returns HTTP 404) and there is no Docker available in this environment, so
these fixtures never attempt to spin up a vehicle themselves - they only
connect to whatever ``DRONEKIT_TEST_CONNECTION`` points at. If the variable
is unset, tests that depend on it are skipped (not failed).
"""

import os
import pathlib
import time

import pytest

import dronekit

# Default timeout (seconds) for connect()'s wait_ready handshake.
DEFAULT_CONNECT_TIMEOUT = 30

# Every test module that lives under this directory gets the "sitl" marker
# applied automatically - see pytest_collection_modifyitems() below.
_SITL_DIR = pathlib.Path(__file__).parent / "sitl"


def wait_for(condition, time_max):
    """Poll ``condition`` (a zero-argument callable) until it returns a
    truthy value, or until ``time_max`` seconds have elapsed - whichever
    comes first. Does not raise on timeout; callers are expected to assert
    on the outcome afterwards.

    This is a plain importable helper (``from dronekit.test.conftest import
    wait_for``) rather than a fixture, since tests use it as an ordinary
    function call inside loops/callbacks, not as a value injected once per
    test.
    """
    time_start = time.time()
    while not condition():
        if time.time() - time_start > time_max:
            break
        time.sleep(0.1)


@pytest.fixture(scope="session")
def sitl_connection_string():
    """The connection string to use for tests that need a live vehicle.

    Reads ``DRONEKIT_TEST_CONNECTION`` from the environment. This can be any
    connection string ``dronekit.connect()`` accepts: SITL over UDP/TCP, or
    a real flight controller over a serial port. If it is not set, the
    requesting test is skipped with an explanatory message - we do not try
    to start a simulator ourselves (there isn't a working one to start).
    """
    connection_string = os.environ.get("DRONEKIT_TEST_CONNECTION")
    if not connection_string:
        pytest.skip(
            "DRONEKIT_TEST_CONNECTION is not set. These tests need a live "
            "vehicle - simulated (e.g. SITL) or real hardware - to talk to. "
            "Set DRONEKIT_TEST_CONNECTION to a connection string accepted "
            "by dronekit.connect(), e.g. 'tcp:127.0.0.1:5760' for SITL over "
            "TCP, 'udp:127.0.0.1:14550' for SITL/companion over UDP, or "
            "'com3' / '/dev/ttyACM0' for a real flight controller over "
            "serial."
        )
    return connection_string


@pytest.fixture
def vehicle(sitl_connection_string):
    """A connected, ready Vehicle for the duration of one test.

    Connects with ``wait_ready=True`` so parameters/attitude/mode/etc. are
    already populated when the test body runs, and always closes the
    connection on teardown, even if the test raises.

    Note on SITL_SPEEDUP / SITL_RATE: these used to be environment variables
    read by dronekit/test/__init__.py to build command-line arguments
    (--speedup, -r) for launching the dronekit-sitl binary. Now that we
    never launch a simulator process ourselves (there's nothing left to
    launch), neither variable has a meaningful equivalent to "pass through"
    here: SITL_SPEEDUP configured the simulator's internal clock speed, which
    doesn't exist as a concept on this side of the MAVLink connection at
    all, and SITL_RATE configured the simulator's own telemetry rate rather
    than the GCS-side stream request rate that connect()'s `rate` parameter
    controls. Wiring either through would be inventing behaviour, so this
    fixture intentionally ignores both.
    """
    v = dronekit.connect(
        sitl_connection_string,
        wait_ready=True,
        timeout=DEFAULT_CONNECT_TIMEOUT,
    )
    try:
        yield v
    finally:
        v.close()


def pytest_collection_modifyitems(config, items):
    """Automatically apply the "sitl" marker to every test collected under
    dronekit/test/sitl/, so nobody has to remember to mark them by hand.

    The marker is still named "sitl" for continuity with the pre-migration
    suite, but it really means "needs a live vehicle, simulated (SITL) or
    real" - it is applied the same way regardless of whether
    DRONEKIT_TEST_CONNECTION ends up pointing at a simulator or at real
    hardware.
    """
    for item in items:
        if _SITL_DIR in item.path.parents:
            item.add_marker(pytest.mark.sitl)
