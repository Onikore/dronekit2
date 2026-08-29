"""Regression tests for task E4's D5/D6/D8/D10 fixes.
"""

import ast
import pathlib

import pytest

import dronekit
import dronekit.mavlink
from dronekit import CommandSequence, Vehicle
from dronekit import TimeoutError as DKTimeoutError


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
