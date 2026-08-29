"""Regression tests for task E4's D5/D6/D8/D10 fixes.

D8 and D10 need a Vehicle instance, but not a live one - Vehicle.__init__
only registers message listener callbacks, it never talks to the network by
itself. So these tests build a real Vehicle around a real (but never
started - no threads, no actual traffic) MAVConnection bound to a local
udpin socket, then drive its message listeners directly by calling
vehicle.notify_message_listeners(name, fake_msg) with small fake message
objects that carry just the fields the listener under test reads. This
exercises the actual production listener closures in dronekit/__init__.py,
not a reimplementation of them.
"""

import ast
import pathlib

import pytest

import dronekit
import dronekit.mavlink
from dronekit import APIException, CommandSequence, Vehicle
from dronekit import TimeoutError as DKTimeoutError
from dronekit.mavlink import MAVConnection

# ---------------------------------------------------------------------------
# D5 - no bare `except:` clauses left in either module
# ---------------------------------------------------------------------------

def _bare_except_lines(module):
    source = pathlib.Path(module.__file__).read_text()
    tree = ast.parse(source)
    return [node.lineno for node in ast.walk(tree)
            if isinstance(node, ast.ExceptHandler) and node.type is None]


def test_no_bare_except_clauses_in_dronekit_init():
    lines = _bare_except_lines(dronekit)
    assert lines == [], (
        "Bare `except:` clauses (swallow BaseException, incl. "
        "KeyboardInterrupt/SystemExit) found at dronekit/__init__.py "
        f"line(s): {lines!r}"
    )


def test_no_bare_except_clauses_in_mavlink_module():
    lines = _bare_except_lines(dronekit.mavlink)
    assert lines == [], (
        f"Bare `except:` clauses found at dronekit/mavlink.py line(s): {lines!r}"
    )


# ---------------------------------------------------------------------------
# D6 - duration measurements use time.monotonic(), not time.time()
# ---------------------------------------------------------------------------

def test_wait_for_timeout_uses_monotonic_not_walltime(monkeypatch):
    def boom():
        raise AssertionError('wait_for() must not call time.time() to measure a timeout')

    monkeypatch.setattr(dronekit.time, 'time', boom)

    with pytest.raises(DKTimeoutError):
        Vehicle.wait_for(None, lambda: False, timeout=0.05, interval=0.02)


class _StubMaster:
    def __init__(self):
        self.calls = []

    def waypoint_clear_all_send(self):
        self.calls.append('clear_all')

    def waypoint_count_send(self, n):
        self.calls.append(('count_send', n))


class _StubWploader:
    def count(self):
        return 1


class _StubVehicleForUpload:
    def __init__(self):
        self._wpts_dirty = True
        self._master = _StubMaster()
        self._wploader = _StubWploader()
        self._wp_uploaded = [False]  # never flips to all-True -> hits timeout


def test_command_sequence_upload_timeout_uses_monotonic_not_walltime(monkeypatch):
    def boom():
        raise AssertionError('upload() timeout must not call time.time()')

    monkeypatch.setattr(dronekit.time, 'time', boom)

    cmds = CommandSequence(_StubVehicleForUpload())
    with pytest.raises(DKTimeoutError):
        cmds.upload(timeout=0.05)


# ---------------------------------------------------------------------------
# Shared fixture / fakes for D8 and D10
# ---------------------------------------------------------------------------

@pytest.fixture
def vehicle():
    handler = MAVConnection('udpin:127.0.0.1:0')
    v = Vehicle(handler)
    try:
        yield v
    finally:
        # handler.close() would block forever waiting for out_queue to
        # drain (nothing is consuming it - the out thread was never
        # started), so release the underlying socket directly instead.
        handler.master.close()


class _FakeMissionCountMsg:
    def __init__(self, count):
        self.count = count

    def get_type(self):
        return 'MISSION_COUNT'


class _FakeMissionItemMsg:
    def __init__(self, seq, x=0, y=0, z=0):
        self.seq = seq
        self.x = x
        self.y = y
        self.z = z

    def get_type(self):
        return 'MISSION_ITEM'


class _FakeGlobalPositionIntMsg:
    def __init__(self, lat, lon, alt, relative_alt):
        self.lat = lat
        self.lon = lon
        self.alt = alt
        self.relative_alt = relative_alt
        # Also read by Vehicle's velocity listener (a separate GLOBAL_POSITION_INT
        # handler unrelated to what's under test here) - fill them in so it
        # doesn't log a spurious AttributeError.
        self.vx = 0
        self.vy = 0
        self.vz = 0

    def get_type(self):
        return 'GLOBAL_POSITION_INT'


def _complete_download(vehicle, n_wp=1):
    """Drive a commands.download() to completion the way the vehicle's
    real MISSION_COUNT/MISSION_ITEM listeners would, given a mission of
    n_wp waypoints (including the home waypoint at seq 0)."""
    vehicle.notify_message_listeners('MISSION_COUNT', _FakeMissionCountMsg(n_wp))
    for seq in range(n_wp):
        vehicle.notify_message_listeners('MISSION_ITEM', _FakeMissionItemMsg(seq))


# ---------------------------------------------------------------------------
# D8 - CommandSequence.__len__/__getitem__ during an in-progress download()
# ---------------------------------------------------------------------------

def test_len_raises_while_download_in_progress(vehicle):
    vehicle.commands.download()
    with pytest.raises(APIException):
        len(vehicle.commands)


def test_getitem_raises_while_download_in_progress(vehicle):
    vehicle.commands.download()
    with pytest.raises(APIException):
        vehicle.commands[0]


def test_len_works_before_any_download():
    """Sanity check: a Vehicle that has never had download() called on it
    (the common case - _wp_download_in_progress defaults to False) must not
    be affected by the guard."""
    handler = MAVConnection('udpin:127.0.0.1:0')
    try:
        v = Vehicle(handler)
        assert len(v.commands) == 0
    finally:
        handler.master.close()


def test_len_and_getitem_work_again_once_download_completes(vehicle):
    vehicle.commands.download()
    assert vehicle._wp_download_in_progress is True

    _complete_download(vehicle, n_wp=1)

    assert vehicle._wp_download_in_progress is False
    assert len(vehicle.commands) == 0  # 1 wp downloaded (home only) -> count() - 1


# ---------------------------------------------------------------------------
# D10 - torn read across Locations' global_frame / global_relative_frame
# ---------------------------------------------------------------------------

def test_global_frame_property_never_returns_a_torn_combination(vehicle):
    """Pre-fix, _lat/_lon/_alt were three separate instance attributes
    updated by three separate statements inside the GLOBAL_POSITION_INT
    listener, and global_frame rebuilt a fresh LocationGlobal from them on
    every read. A reader thread calling vehicle.location.global_frame in
    between those statements could observe a torn combination (e.g. new
    lat/lon paired with the previous message's alt). This test can't
    reliably win that race deterministically in a unit test, so instead it
    pins down the fix's actual mechanism: global_frame/global_relative_frame
    are whole cached objects replaced by a single attribute assignment, so
    the property must return either the fully-previous or fully-current
    object - it must always be internally consistent with *some* message
    that was actually received.
    """
    vehicle.notify_message_listeners(
        'GLOBAL_POSITION_INT', _FakeGlobalPositionIntMsg(lat=12345670, lon=76543210, alt=1000, relative_alt=500))
    first = vehicle.location.global_frame
    assert (first.lat, first.lon, first.alt) == (1.234567, 7.654321, 1.0)

    vehicle.notify_message_listeners(
        'GLOBAL_POSITION_INT', _FakeGlobalPositionIntMsg(lat=20000000, lon=80000000, alt=2000, relative_alt=600))
    second = vehicle.location.global_frame
    assert (second.lat, second.lon, second.alt) == (2.0, 8.0, 2.0)

    # The object returned by an earlier read must not have been mutated by
    # a later message - each update must produce a brand new object rather
    # than mutating shared state in place.
    assert (first.lat, first.lon, first.alt) == (1.234567, 7.654321, 1.0)


def test_global_frame_read_returns_a_copy_not_the_live_cached_object(vehicle):
    """Mirrors Vehicle.home_location's existing copy.copy() pattern:
    mutating what a caller reads back must not corrupt the cached value
    that the next reader sees."""
    vehicle.notify_message_listeners(
        'GLOBAL_POSITION_INT', _FakeGlobalPositionIntMsg(lat=1000000, lon=2000000, alt=100, relative_alt=50))

    frame = vehicle.location.global_frame
    frame.alt = 99999

    assert vehicle.location.global_frame.alt == 0.1


def test_global_relative_frame_updates_on_every_message_independent_of_alt_gate():
    handler = MAVConnection('udpin:127.0.0.1:0')
    try:
        v = Vehicle(handler)
        # alt=0 on the very first message means the global_frame "require
        # non-zero first alt" gate never fires, but global_relative_frame
        # must still update - it isn't gated at all.
        v.notify_message_listeners(
            'GLOBAL_POSITION_INT', _FakeGlobalPositionIntMsg(lat=1000000, lon=2000000, alt=0, relative_alt=250))
        rel = v.location.global_relative_frame
        assert (rel.lat, rel.lon, rel.alt) == (0.1, 0.2, 0.25)
        assert v.location.global_frame.alt is None  # gate never opened
    finally:
        handler.master.close()
