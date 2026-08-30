import time
from contextlib import contextmanager

from pymavlink import mavutil


@contextmanager
def assert_command_ack(vehicle, command_type, ack_result=mavutil.mavlink.MAV_RESULT_ACCEPTED, timeout=10):
    """Context manager to assert that:

    1) exactly one COMMAND_ACK is received from a Vehicle;
    2) for a specific command type;
    3) with a result in the given set (a single value, or an iterable of acceptable values -
       some commands, e.g. sensor calibration in a stationary SITL, were confirmed against live
       SITL to legitimately return different results run to run depending on real-time
       simulation state, not because of a test bug);
    4) within a timeout (in seconds).

    For example:

    .. code-block:: python

        with assert_command_ack(vehicle, mavutil.mavlink.MAV_CMD_PREFLIGHT_CALIBRATION, timeout=30):
            vehicle.calibrate_gyro()

    """
    acceptable_results = ack_result if isinstance(ack_result, (set, frozenset, tuple, list)) else {ack_result}

    acks = []

    def on_ack(self, name, message):
        if message.command == command_type:
            acks.append(message)

    vehicle.add_message_listener("COMMAND_ACK", on_ack)

    yield

    start_time = time.time()
    while not acks and time.time() - start_time < timeout:
        time.sleep(0.1)
    vehicle.remove_message_listener("COMMAND_ACK", on_ack)

    assert len(acks) == 1, f"expected exactly one ACK for command {command_type}, got {acks}"
    assert acks[0].command == command_type, f"expected ACK for command {command_type}, got {acks[0]}"
    assert acks[0].result in acceptable_results, (
        f"expected result in {acceptable_results} for command {command_type}, got {acks[0].result}"
    )
