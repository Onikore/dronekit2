import time
from contextlib import contextmanager

from pymavlink import mavutil


@contextmanager
def assert_command_ack(vehicle, command_type, ack_result=mavutil.mavlink.MAV_RESULT_ACCEPTED, timeout=10):
    """Context manager to assert that:

    1) exactly one COMMAND_ACK is received from a Vehicle;
    2) for a specific command type;
    3) with the given result;
    4) within a timeout (in seconds).

    For example:

    .. code-block:: python

        with assert_command_ack(vehicle, mavutil.mavlink.MAV_CMD_PREFLIGHT_CALIBRATION, timeout=30):
            vehicle.calibrate_gyro()

    """

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

    assert len(acks) == 1  # one and only one ACK
    assert acks[0].command == command_type  # for the correct command
    assert acks[0].result == ack_result  # the result must be successful
