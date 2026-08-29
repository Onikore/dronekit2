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
        "line(s): %r" % lines
    )


def test_no_bare_except_clauses_in_mavlink_module():
    lines = _bare_except_lines(dronekit.mavlink)
    assert lines == [], (
        "Bare `except:` clauses found at dronekit/mavlink.py line(s): %r" % lines
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
