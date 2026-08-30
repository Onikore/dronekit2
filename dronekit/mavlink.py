from __future__ import annotations

import atexit
import copy
import errno
import logging
import os
import socket
import sys
import time
import weakref
from queue import Empty, Queue
from threading import Thread
from typing import Any, Callable

from pymavlink import mavutil

from dronekit import APIException

if sys.platform == "win32":
    from errno import WSAECONNRESET as ECONNABORTED
else:
    from errno import ECONNABORTED


class MAVWriter:
    """
    Indirection layer to take messages written to MAVlink and send them all
    on the same thread.
    """

    def __init__(self, queue: Queue) -> None:
        self._logger = logging.getLogger(__name__)
        self.queue = queue

    def write(self, pkt: Any) -> None:
        self.queue.put(pkt)

    def read(self) -> None:
        self._logger.critical("writer should not have had a read request")
        os._exit(43)


class mavudpin_multi(mavutil.mavfile):
    """a UDP mavlink socket"""

    def __init__(
        self,
        device: str,
        baud: int | None = None,
        input: bool = True,
        broadcast: bool = False,
        source_system: int = 255,
        source_component: int = 0,
        use_native: bool = mavutil.default_native,
    ) -> None:
        self._logger = logging.getLogger(__name__)
        a = device.split(":")
        if len(a) != 2:
            self._logger.critical("UDP ports must be specified as host:port")
            sys.exit(1)
        self.port = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_server = input
        self.broadcast = False
        self.addresses: set[Any] = set()
        if input:
            self.port.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.port.bind((a[0], int(a[1])))
        else:
            self.destination_addr = (a[0], int(a[1]))
            if broadcast:
                self.port.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                self.broadcast = True
        mavutil.set_close_on_exec(self.port.fileno())
        self.port.setblocking(False)
        mavutil.mavfile.__init__(
            self,
            self.port.fileno(),
            device,
            source_system=source_system,
            source_component=source_component,
            input=input,
            use_native=use_native,
        )

    def close(self) -> None:
        self.port.close()

    def recv(self, n: int | None = None) -> bytes | None:
        try:
            try:
                data, new_addr = self.port.recvfrom(65535)
            except OSError as e:
                if e.errno in [errno.EAGAIN, errno.EWOULDBLOCK, errno.ECONNREFUSED]:
                    return b""
                # Any other socket error is unexpected - re-raise it so it is
                # handled (and logged with its real type) by the except
                # Exception clause below, instead of falling through to
                # reference the undefined `new_addr`.
                raise
            if self.udp_server:
                self.addresses.add(new_addr)
            elif self.broadcast:
                self.addresses = {new_addr}
            return data
        except Exception:
            self._logger.exception("Exception while reading data", exc_info=True)
            return None

    def write(self, buf: bytes) -> None:
        try:
            try:
                if self.udp_server:
                    for addr in self.addresses:
                        self.port.sendto(buf, addr)
                else:
                    if len(self.addresses) and self.broadcast:
                        # self.addresses is a set - pick an arbitrary (the
                        # only, in practice) element rather than indexing it.
                        self.destination_addr = next(iter(self.addresses))
                        self.broadcast = False
                        self.port.connect(self.destination_addr)
                    self.port.sendto(buf, self.destination_addr)
            except OSError:
                pass
        except Exception:
            self._logger.exception("Exception while writing data", exc_info=True)

    def recv_msg(self) -> Any:
        """message receive routine for UDP link"""
        self.pre_message()
        s = self.recv()
        if s and len(s) > 0:
            if self.first_byte:
                self.auto_mavlink_version(s)

        m = self.mav.parse_char(s)
        if m is not None:
            self.post_message(m)

        return m


class MAVConnection:
    # Declared at class level (rather than solely via the inline
    # `self.mavlink_thread_in: Thread | None = t` in __init__) because
    # stop_threads() below - which reassigns these to None - appears
    # earlier in the class body than __init__. Without an authoritative
    # class-level type, mypy infers the attribute's type from whichever
    # assignment it sees first while walking the class, lands on
    # `self.mavlink_thread_in = None` in stop_threads, and then reports
    # the real __init__ assignment as an incompatible redefinition.
    mavlink_thread_in: Thread | None
    mavlink_thread_out: Thread | None

    def stop_threads(self) -> None:
        # Thread.join() raises RuntimeError if called on a thread that was
        # never started (e.g. close()/atexit fires before start() was ever
        # called). Thread.ident is None until start() has run, so use it as
        # the "was this thread actually started" guard.
        if self.mavlink_thread_in is not None:
            if self.mavlink_thread_in.ident is not None:
                self.mavlink_thread_in.join()
            self.mavlink_thread_in = None
        if self.mavlink_thread_out is not None:
            if self.mavlink_thread_out.ident is not None:
                self.mavlink_thread_out.join()
            self.mavlink_thread_out = None

    def __init__(
        self,
        ip: str,
        baud: int = 115200,
        target_system: int = 0,
        source_system: int = 255,
        source_component: int = 0,
        use_native: bool = False,
    ) -> None:
        self._logger = logging.getLogger(__name__)

        if ip.startswith("udpin:"):
            self.master: Any = mavudpin_multi(
                ip[6:], input=True, baud=baud, source_system=source_system, source_component=source_component
            )
        else:
            self.master = mavutil.mavlink_connection(
                ip, baud=baud, source_system=source_system, source_component=source_component
            )

        # TODO get rid of "master" object as exposed,
        # keep it private, expose something smaller for dronekit
        self.out_queue: Queue = Queue()
        self.master.mav = mavutil.mavlink.MAVLink(
            MAVWriter(self.out_queue),
            srcSystem=self.master.source_system,
            srcComponent=self.master.source_component,
            use_native=use_native,
        )

        # Monkey-patch MAVLink object for fix_targets.
        sendfn = self.master.mav.send

        def newsendfn(mavmsg: Any, *args: Any, **kwargs: Any) -> Any:
            self.fix_targets(mavmsg)
            return sendfn(mavmsg, *args, **kwargs)

        self.master.mav.send = newsendfn

        # Targets
        self.target_system = target_system

        # Listeners.
        self.loop_listeners: list[Callable[..., Any]] = []
        self.message_listeners: list[Callable[..., Any]] = []

        # Debug flag.
        self._accept_input = True
        self._alive = True
        self._death_error: Exception | None = None

        # Use a weak reference in the atexit callback so that a MAVConnection
        # (and everything it holds: threads, sockets, the whole Vehicle
        # graph via back-references) remains collectable once the caller
        # drops their references and/or calls close() - atexit.register()
        # would otherwise keep this object alive for the life of the
        # interpreter even after close().
        self_ref = weakref.ref(self)

        def onexit() -> None:
            conn = self_ref()
            if conn is not None:
                conn._alive = False
                conn.stop_threads()

        self._onexit = onexit
        atexit.register(onexit)

        def mavlink_thread_out() -> None:
            # Huge try catch in case we see http://bugs.python.org/issue1856
            try:
                while self._alive:
                    try:
                        msg = self.out_queue.get(True, timeout=0.01)
                        self.master.write(msg)
                    except Empty:
                        continue
                    except OSError as error:
                        # If connection reset (closed), stop polling.
                        if error.errno == ECONNABORTED:
                            raise APIException("Connection aborting during read") from error
                        raise
                    except Exception as e:
                        self._logger.exception(f"mav send error: {str(e)}")
                        break
            except APIException as e:
                self._logger.exception("Exception in MAVLink write loop", exc_info=True)
                self._alive = False
                self.master.close()
                self._death_error = e

            except Exception as e:
                # http://bugs.python.org/issue1856
                if not self._alive:
                    pass
                else:
                    self._alive = False
                    self.master.close()
                    self._death_error = e

            # Explicitly clear out buffer so .close closes.
            self.out_queue = Queue()

        def mavlink_thread_in() -> None:
            # Huge try catch in case we see http://bugs.python.org/issue1856
            try:
                while self._alive:
                    # Loop listeners.
                    for fn in self.loop_listeners:
                        fn(self)

                    # Sleep
                    self.master.select(0.05)

                    while self._accept_input:
                        try:
                            msg = self.master.recv_msg()
                        except OSError as error:
                            # If connection reset (closed), stop polling.
                            if error.errno == ECONNABORTED:
                                raise APIException("Connection aborting during send") from error
                            raise
                        except mavutil.mavlink.MAVError as e:
                            # Avoid
                            #   invalid MAVLink prefix '73'
                            #   invalid MAVLink prefix '13'
                            self._logger.debug(f"mav recv error: {str(e)}")
                            msg = None
                        except Exception:
                            # Log any other unexpected exception
                            self._logger.exception("Exception while receiving message: ", exc_info=True)
                            msg = None
                        if not msg:
                            break

                        # Message listeners.
                        for fn in self.message_listeners:
                            try:
                                fn(self, msg)
                            except Exception:
                                self._logger.exception(
                                    f"Exception in message handler for {msg.get_type()}", exc_info=True
                                )

            except APIException as e:
                self._logger.exception("Exception in MAVLink input loop")
                self._alive = False
                self.master.close()
                self._death_error = e
                return

            except Exception as e:
                # http://bugs.python.org/issue1856
                if not self._alive:
                    pass
                else:
                    self._alive = False
                    self.master.close()
                    self._death_error = e

        t = Thread(target=mavlink_thread_in)
        t.daemon = True
        self.mavlink_thread_in = t

        t = Thread(target=mavlink_thread_out)
        t.daemon = True
        self.mavlink_thread_out = t

    def reset(self) -> None:
        self.out_queue = Queue()
        if hasattr(self.master, "reset"):
            self.master.reset()
        else:
            try:
                self.master.close()
            except Exception:
                pass
            self.master = mavutil.mavlink_connection(self.master.address)

    def fix_targets(self, message: Any) -> None:
        """Set correct target IDs for our vehicle"""
        if hasattr(message, "target_system"):
            message.target_system = self.target_system

    def forward_loop(self, fn: Callable[..., Any]) -> None:
        """
        Decorator for event loop.
        """
        self.loop_listeners.append(fn)

    def forward_message(self, fn: Callable[..., Any]) -> None:
        """
        Decorator for message inputs.
        """
        self.message_listeners.append(fn)

    def start(self) -> None:
        # mavlink_thread_in/out are always real Thread objects here in
        # practice (set at the end of __init__, only ever reset to None
        # by stop_threads()/close() - and nothing in this codebase calls
        # start() again after close()). Pre-existing dynamic invariant,
        # not re-verified here to avoid changing behavior for a typing pass.
        if not self.mavlink_thread_in.is_alive():  # type: ignore[union-attr]
            self.mavlink_thread_in.start()  # type: ignore[union-attr]
        if not self.mavlink_thread_out.is_alive():  # type: ignore[union-attr]
            self.mavlink_thread_out.start()  # type: ignore[union-attr]

    def close(self) -> None:
        # TODO this can block forever if parameters continue to be added
        self._alive = False
        while not self.out_queue.empty():
            time.sleep(0.1)
        self.stop_threads()
        self.master.close()
        # A properly closed connection should not leave a dangling atexit
        # entry around (see the weakref note in __init__).
        atexit.unregister(self._onexit)

    def pipe(self, target: MAVConnection) -> MAVConnection:
        target.target_system = self.target_system

        # vehicle -> self -> target
        @self.forward_message
        def callback(_: Any, msg: Any) -> None:
            try:
                target.out_queue.put(msg.pack(target.master.mav))
            except Exception:
                try:
                    assert len(msg.get_msgbuf()) > 0
                    target.out_queue.put(msg.get_msgbuf())
                except Exception:
                    self._logger.exception(f"Could not pack this object on receive: {type(msg)}", exc_info=True)

        # target -> self -> vehicle
        @target.forward_message
        def callback(_: Any, msg: Any) -> None:  # noqa: F811 - consumed immediately by the decorator above, not a real redefinition
            msg = copy.copy(msg)
            target.fix_targets(msg)
            try:
                self.out_queue.put(msg.pack(self.master.mav))
            except Exception:
                try:
                    assert len(msg.get_msgbuf()) > 0
                    self.out_queue.put(msg.get_msgbuf())
                except Exception:
                    self._logger.exception(f"Could not pack this object on forward: {type(msg)}", exc_info=True)

        return target
