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

tcp_conn = mavutil.mavlink_connection(f"tcp:{TCP_ADDR[0]}:{TCP_ADDR[1]}")
# No explicit bind: the OS assigns this socket a stable ephemeral local
# port on first use, which is fine - clients learn our address from the
# first packet they receive from us and reply there.
udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_sock.settimeout(1.0)


def udp_to_tcp():
    while True:
        try:
            data, _addr = udp_sock.recvfrom(4096)
        except socket.timeout:
            continue
        except OSError:
            # e.g. a stale client's port becoming unreachable (ICMP) between
            # tests - transient, not fatal to the relay itself.
            continue
        try:
            tcp_conn.write(data)
        except OSError:
            pass


def tcp_to_udp():
    while True:
        msg = tcp_conn.recv_match(blocking=True, timeout=1)
        if msg is None:
            continue
        try:
            udp_sock.sendto(msg.get_msgbuf(), UDP_DEST)
        except OSError:
            pass


if __name__ == "__main__":
    threading.Thread(target=udp_to_tcp, daemon=True).start()
    print(f"relay: tcp:{TCP_ADDR[0]}:{TCP_ADDR[1]} <-> udp (sending to {UDP_DEST[0]}:{UDP_DEST[1]})", flush=True)
    tcp_to_udp()
