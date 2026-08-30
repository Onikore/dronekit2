import time


def test_reboot(vehicle):
    """Tries to reboot the vehicle, and checks that the autopilot ACKs the command."""

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
