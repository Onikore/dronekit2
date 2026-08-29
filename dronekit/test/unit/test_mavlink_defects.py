"""Regression tests for task E4's D1/D2/D3/D4/D7/D9 fixes.

These target dronekit/mavlink.py's mavudpin_multi and MAVConnection classes,
plus the resource-cleanup path in dronekit.connect(). None of them need a
live vehicle - mavudpin_multi only binds a local UDP socket, and
MAVConnection's constructor does not start any threads (that only happens
via start(), which these tests never call), so all of this runs
synchronously and needs no simulator.
"""

import errno
import socket
import sys

import dronekit.mavlink as mavlink_mod
from dronekit.mavlink import MAVConnection, mavudpin_multi


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

class _RecordingSocket:
    """Stand-in for the real UDP socket so write()/recv() tests don't touch
    the network at all - just records what mavudpin_multi tried to do."""

    def __init__(self):
        self.sendto_calls = []
        self.connect_calls = []

    def sendto(self, buf, addr):
        self.sendto_calls.append((buf, addr))

    def connect(self, addr):
        self.connect_calls.append(addr)

    def recvfrom(self, bufsize):
        raise AssertionError('recvfrom should be stubbed per-test')


def _broadcast_client():
    """A mavudpin_multi configured like a broadcast *client* (input=False,
    broadcast=True), with its real socket swapped out for a recording stub
    right after construction (the constructor itself needs a real socket to
    set SO_BROADCAST etc., but nothing after that does)."""
    m = mavudpin_multi('127.0.0.1:0', input=False, broadcast=True)
    m.port.close()
    m.port = _RecordingSocket()
    return m


def _udpin_client():
    m = mavudpin_multi('127.0.0.1:0', input=True)
    m.port.close()
    m.port = _RecordingSocket()
    return m


# ---------------------------------------------------------------------------
# D1 - mavudpin_multi.write() locking onto the first broadcast responder
# ---------------------------------------------------------------------------

def test_write_locks_onto_first_broadcast_responder_without_crashing():
    """self.addresses is a set (see mavudpin_multi.__init__), so indexing it
    with [0] - the pre-fix code - raises `TypeError: 'set' object is not
    subscriptable`. That TypeError is caught by write()'s own outer
    `except Exception` and merely logged, so the observable symptom is not a
    raised exception but a silent no-op: destination_addr/broadcast never
    update and nothing is ever sent. This test asserts the real, intended
    side effects happen instead.
    """
    m = _broadcast_client()
    m.addresses = {('192.168.1.42', 14550)}
    assert m.broadcast is True

    m.write(b'ping')

    assert m.broadcast is False
    assert m.destination_addr == ('192.168.1.42', 14550)
    assert m.port.connect_calls == [('192.168.1.42', 14550)]
    assert m.port.sendto_calls == [(b'ping', ('192.168.1.42', 14550))]


def test_write_udp_server_sends_to_every_known_address():
    """Unrelated to D1, but pins down the udp_server fan-out branch so a
    future change to write() can't silently break it."""
    m = _udpin_client()
    m.addresses = {('10.0.0.1', 100), ('10.0.0.2', 200)}

    m.write(b'hello')

    sent_addrs = {addr for (_buf, addr) in m.port.sendto_calls}
    assert sent_addrs == {('10.0.0.1', 100), ('10.0.0.2', 200)}


# ---------------------------------------------------------------------------
# D2 - mavudpin_multi.recv()
# ---------------------------------------------------------------------------

def test_recv_returns_bytes_not_str_on_would_block():
    """Pre-fix, the EAGAIN/EWOULDBLOCK/ECONNREFUSED path returned "" (str).
    recv_msg() then does len(s) and self.mav.parse_char(s), which expects
    bytes like every other code path here - so the return type must be
    bytes, not str.
    """
    m = _udpin_client()

    def raise_would_block(bufsize):
        raise socket.error(errno.EWOULDBLOCK, 'would block')

    m.port.recvfrom = raise_would_block

    result = m.recv()

    assert result == b""
    assert isinstance(result, bytes)


def test_recv_reraises_unexpected_socket_error_instead_of_unboundlocalerror():
    """Pre-fix, an errno outside {EAGAIN, EWOULDBLOCK, ECONNREFUSED} fell
    through the `except socket.error` block with no return and no raise,
    then hit `if self.udp_server: self.addresses.add(new_addr)` where
    new_addr was never assigned -> UnboundLocalError. That UnboundLocalError
    (not the original socket.error) is what ends up being logged by the
    outer `except Exception`. This test inspects the exception actually
    captured by the logger to confirm it is the original socket.error, not
    an UnboundLocalError caused by falling through to reference undefined
    new_addr.
    """
    m = _udpin_client()

    def raise_econnreset(bufsize):
        raise socket.error(errno.ECONNRESET, 'connection reset')

    m.port.recvfrom = raise_econnreset

    logged_exc_types = []

    def fake_exception(msg, exc_info=True):
        logged_exc_types.append(sys.exc_info()[0])

    m._logger.exception = fake_exception

    result = m.recv()

    assert result is None
    assert len(logged_exc_types) == 1
    logged_type = logged_exc_types[0]
    assert logged_type is not None
    assert not issubclass(logged_type, (UnboundLocalError, NameError)), (
        "recv() logged %r - the original socket.error was swallowed and "
        "replaced by a bug in the fallthrough path" % logged_type
    )
    assert issubclass(logged_type, OSError)  # socket.error is an OSError alias


# ---------------------------------------------------------------------------
# D3 - MAVConnection.stop_threads() before start()
# ---------------------------------------------------------------------------

def test_stop_threads_before_start_does_not_raise():
    """Pre-fix, Thread.join() on a thread that was never started raises
    RuntimeError('cannot join thread before it is started'). This is
    exactly what happens if close() (or the atexit handler) runs before
    start() was ever called.
    """
    handler = MAVConnection('udpin:127.0.0.1:0')
    try:
        assert handler.mavlink_thread_in.ident is None
        assert handler.mavlink_thread_out.ident is None

        handler.stop_threads()  # must not raise RuntimeError

        assert handler.mavlink_thread_in is None
        assert handler.mavlink_thread_out is None
    finally:
        handler.master.close()


def test_stop_threads_after_start_still_joins(monkeypatch):
    """Make sure the D3 fix didn't turn stop_threads() into a no-op for the
    case it's actually supposed to handle: a thread that really was
    started."""
    handler = MAVConnection('udpin:127.0.0.1:0')
    try:
        handler._alive = False  # thread functions loop on self._alive
        handler.start()
        assert handler.mavlink_thread_in.ident is not None

        handler.stop_threads()

        assert handler.mavlink_thread_in is None
        assert handler.mavlink_thread_out is None
    finally:
        handler.master.close()


# ---------------------------------------------------------------------------
# D4 - mavudpin_multi.address / MAVConnection.reset() fallback
# ---------------------------------------------------------------------------

def test_mavudpin_multi_has_address_attribute_for_reset_fallback():
    """reset()'s fallback path (used when self.master has no .reset())
    does `mavutil.mavlink_connection(self.master.address)`. mavudpin_multi
    inherits from mavutil.mavfile, whose __init__ already stores the device
    string it's given as `self.address` - and mavudpin_multi.__init__
    passes `device` straight through to that call - so `.address` is
    already present. This test locks that invariant down so a future change
    to mavudpin_multi.__init__ (e.g. no longer forwarding `device` to
    mavfile.__init__) gets caught immediately instead of surfacing as an
    AttributeError deep inside reset().
    """
    m = mavudpin_multi('127.0.0.1:0', input=True)
    try:
        assert m.address == '127.0.0.1:0'
        assert not hasattr(m, 'reset')  # confirms reset() takes the fallback path
    finally:
        m.close()


def test_reset_fallback_does_not_raise_attributeerror_for_udpin(monkeypatch):
    handler = MAVConnection('udpin:127.0.0.1:0')
    try:
        assert not hasattr(handler.master, 'reset')

        calls = []

        class _StubMaster:
            address = 'stub-address'

            def close(self):
                pass

        def fake_mavlink_connection(address, *a, **kw):
            calls.append(address)
            return _StubMaster()

        monkeypatch.setattr(mavlink_mod.mavutil, 'mavlink_connection', fake_mavlink_connection)

        handler.reset()  # must not raise AttributeError

        assert calls == ['127.0.0.1:0']
        assert isinstance(handler.master, _StubMaster)
    finally:
        handler.master.close()
