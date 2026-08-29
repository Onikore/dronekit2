import time
import socket
from dronekit import connect


def test_timeout(sitl_connection_string):
    # Connect with timeout of 10s.
    vehicle = connect(sitl_connection_string, wait_ready=True, heartbeat_timeout=20)

    try:
        # Stall input.
        vehicle._handler._accept_input = False

        start = time.time()
        while vehicle._handler._alive and time.time() - start < 30:
            time.sleep(.1)

        assert vehicle._handler._alive is False
    finally:
        vehicle.close()


def test_timeout_empty():
    # Create a dummy server.
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('127.0.0.1', 5760))
    s.listen(1)

    try:
        # Connect with timeout of 10s.
        vehicle = connect('tcp:127.0.0.1:5760', wait_ready=True, heartbeat_timeout=20)

        vehicle.close()

        # Should not pass
        assert False
    except AssertionError:
        raise
    except Exception:
        pass
    finally:
        s.close()
