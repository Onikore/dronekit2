import time

from pymavlink import mavutil


def test_reboot(vehicle):
    """Tries to reboot the vehicle, and checks that the autopilot ACKs the command."""

    # The autopilot correctly refuses to reboot while armed - confirmed
    # against live SITL. Tests share one persistent SITL process for the
    # whole run, and an earlier flight test (e.g. test_goto's RTL) may not
    # have finished landing/disarming by the time this test runs, so force
    # disarm first (param2=21196 is MAVLink's documented magic value for
    # bypassing the normal safety checks, the same one real GCS software
    # uses for emergency disarm) rather than assuming a clean starting state.
    if vehicle.armed:
        msg = vehicle.message_factory.command_long_encode(
            vehicle._handler.target_system,
            0,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
            0,
            0,
            21196,
            0,
            0,
            0,
            0,
            0,
        )
        vehicle.send_mavlink(msg)
        i = 20
        while vehicle.armed and i > 0:
            time.sleep(0.5)
            i -= 1

    reboot_acks = []

    def on_ack(self, name, message):
        if message.command == 246:  # reboot/shutdown
            reboot_acks.append(message)

    vehicle.add_message_listener("COMMAND_ACK", on_ack)
    vehicle.reboot()
    time.sleep(0.5)
    vehicle.remove_message_listener("COMMAND_ACK", on_ack)

    assert len(reboot_acks) == 1  # one and only one ACK
    assert reboot_acks[0].command == 246  # for the correct command
    assert reboot_acks[0].result == 0  # the result must be successful
