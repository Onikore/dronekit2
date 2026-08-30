#!/usr/bin/env python
"""Minimal TCP<->UDP MAVLink relay used by the CI "sitl" job.

ArduPilot's SITL binary, run directly without sim_vehicle.py/MAVProxy in
front of it, accepts exactly one TCP connection for the entire life of the
process (confirmed against real CI runs: the first connection got
ConnectionResetError, and every attempt after it got ConnectionRefusedError
- the server had stopped accepting entirely, not just dropping one client).
That's fatal for dronekit/test/conftest.py's `vehicle` fixture, which opens
a fresh connection per test.

This script becomes the one TCP client SITL will ever accept, and
rebroadcasts everything over UDP, which has no such per-connection limit -
any number of sequential tests can each independently connect, get a
heartbeat, and close. See .github/workflows/ci.yml's "sitl" job for how
it's launched, and why a full MAVProxy install was rejected instead (it
imports wx unconditionally even in --daemon --non-interactive mode - a
known, still-open upstream issue - which would require system GTK
packages this job has no reason to carry).
"""

import socket
import threading
import time

from pymavlink import mavutil

TCP_ADDR = ("127.0.0.1", 5760)
# pymavlink's plain "udp:host:port" connection string defaults to
# input=True (bind/listen semantics), matching how every normal MAVLink
# UDP GCS client - including dronekit.connect(), which is what actually
# uses this - behaves: it binds this fixed port itself and waits for the
# autopilot to send it something first. So this relay must NOT bind this
# port (that would collide with the client trying to bind the same port);
# it must actively send *to* it instead, the way an autopilot does.
UDP_DEST = ("127.0.0.1", 14550)


def log(msg):
    # Two failed attempts at fixing this job's "sitl" step blind (9b9d769,
    # b98731e, 522d6c7) without enough visibility into what was actually
    # happening led to two more silent-guess iterations. This timestamps
    # every relay lifecycle event explicitly so the next failure (if there
    # is one) can be diagnosed from evidence instead of another guess.
    print(f"[relay {time.monotonic():.3f}] {msg}", flush=True)


log(f"connecting to arducopter over tcp:{TCP_ADDR[0]}:{TCP_ADDR[1]} ...")
_connect_start = time.monotonic()
tcp_conn = mavutil.mavlink_connection(f"tcp:{TCP_ADDR[0]}:{TCP_ADDR[1]}")
log(f"tcp connect() returned after {time.monotonic() - _connect_start:.3f}s")
# pymavlink's mavfile/MAVLink objects are not thread-safe: three different
# threads here each touch tcp_conn (this one reads, tcp_heartbeat() and
# udp_to_tcp() both write), and a real CI run showed the actual failure
# mode of that - EOF on TCP socket arriving in bursts of ~20 (matching
# tcp_to_udp()'s 0.05s poll interval) immediately after each
# heartbeat_send() call, meaning arducopter was closing the connection on
# receiving something it couldn't parse as valid MAVLink. Concurrent,
# unsynchronized read()/write() calls on the same socket/parser-state
# object interleaving their bytes explains that precisely - confirmed as
# the working theory only after the earlier heartbeat and buffering fixes
# were verified NOT to be the (whole) story. A local end-to-end test never
# caught this because its fake server just discards received bytes without
# parsing them as MAVLink at all.
tcp_lock = threading.Lock()
# No explicit bind: the OS assigns this socket a stable ephemeral local
# port on first use, which is fine - clients learn our address from the
# first packet they receive from us and reply there.
udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_sock.settimeout(1.0)

_first_udp_from_client = True
_first_tcp_msg = True
_heartbeats_sent = 0


def udp_to_tcp():
    global _first_udp_from_client
    while True:
        try:
            data, addr = udp_sock.recvfrom(4096)
        except socket.timeout:
            continue
        except OSError as e:
            # e.g. a stale client's port becoming unreachable (ICMP) between
            # tests - transient, not fatal to the relay itself.
            log(f"udp recvfrom() OSError (transient, continuing): {e!r}")
            continue
        if _first_udp_from_client:
            log(f"first UDP packet ever received, from {addr}, {len(data)} bytes - forwarding to TCP")
            _first_udp_from_client = False
        try:
            with tcp_lock:
                tcp_conn.write(data)
        except OSError as e:
            log(f"tcp_conn.write() OSError: {e!r}")


def tcp_to_udp():
    # blocking=True here would trust pymavlink's own select()-based
    # throttling, which does not throttle at all once the socket is EOF'd -
    # select() reports an EOF'd socket "readable" immediately forever - so a
    # single dead TCP connection could spin this loop at full CPU speed
    # forever, flooding the log at thousands of lines/second (this exact bug
    # was hit and fixed in an earlier diagnostic version of the wait-for-
    # heartbeat step this relay replaced; it's fixed here the same way).
    # blocking=False plus our own explicit sleep bounds the worst case to a
    # few log lines per second regardless of what the socket is doing - if
    # ArduPilot really does close the one connection it will ever accept,
    # there is nothing to reconnect to, so all this relay can do is log
    # quietly and keep idling rather than spin.
    global _first_tcp_msg
    eof_count = 0
    last_eof_log = 0.0
    while True:
        with tcp_lock:
            msg = tcp_conn.recv_match(type=None, blocking=False)
        if msg is None:
            time.sleep(0.05)
            continue
        if msg.get_type() == "BAD_DATA":
            # pymavlink's handle_eof()/handle_disconnect() print their own
            # unconditional message and return None from recv() - they
            # don't surface as a BAD_DATA msg or raise, so this branch is
            # currently unreachable, but kept as a documented non-goal:
            # this relay does not attempt to distinguish "no data yet" from
            # "socket is dead" beyond what its own throttled loop already
            # bounds, since ArduPilot accepts only one TCP connection ever
            # - there is nothing to reconnect to either way.
            eof_count += 1
            now = time.monotonic()
            if now - last_eof_log > 5:
                log(f"BAD_DATA from tcp_conn ({eof_count} total so far)")
                last_eof_log = now
            continue
        if _first_tcp_msg:
            log(f"first real MAVLink message from arducopter: {msg.get_type()}")
            _first_tcp_msg = False
        try:
            udp_sock.sendto(msg.get_msgbuf(), UDP_DEST)
        except OSError as e:
            log(f"udp_sock.sendto() OSError: {e!r}")


def tcp_heartbeat():
    # Send a GCS heartbeat to the autopilot ourselves, independent of
    # whether any real UDP client has connected to us yet. Reasoned from an
    # earlier, unrelated finding: ArduPilot's serial-over-TCP emulation
    # appears to treat a silently-connected client as a dead line and close
    # it - dronekit's own Vehicle sends exactly this heartbeat once
    # connected (see dronekit/vehicle.py:465), so a real dronekit client
    # never hits this, but this relay is the one holding the TCP side open
    # before any dronekit client exists, so it needs to do the same thing
    # itself from the moment it connects.
    global _heartbeats_sent
    while True:
        try:
            with tcp_lock:
                tcp_conn.mav.heartbeat_send(
                    mavutil.mavlink.MAV_TYPE_GCS, mavutil.mavlink.MAV_AUTOPILOT_INVALID, 0, 0, 0
                )
            _heartbeats_sent += 1
            if _heartbeats_sent <= 3:
                log(f"sent GCS heartbeat #{_heartbeats_sent} to arducopter")
        except OSError as e:
            log(f"tcp_conn.mav.heartbeat_send() OSError: {e!r}")
        time.sleep(1)


if __name__ == "__main__":
    threading.Thread(target=udp_to_tcp, daemon=True).start()
    threading.Thread(target=tcp_heartbeat, daemon=True).start()
    log(f"relay running: tcp:{TCP_ADDR[0]}:{TCP_ADDR[1]} <-> udp (sending to {UDP_DEST[0]}:{UDP_DEST[1]})")
    tcp_to_udp()
