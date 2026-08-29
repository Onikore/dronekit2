import time

from dronekit import VehicleMode


def test_115(vehicle):
    v = vehicle

    # Dummy callback
    def mavlink_callback(*args):
        mavlink_callback.count += 1

    mavlink_callback.count = 0

    # Set the callback.
    v.add_message_listener('*', mavlink_callback)

    # Change the vehicle into STABILIZE mode
    v.mode = VehicleMode("STABILIZE")
    # NOTE wait crudely for ACK on mode update
    time.sleep(3)

    # Expect the callback to have been called
    assert mavlink_callback.count > 0

    # Unset the callback.
    v.remove_message_listener('*', mavlink_callback)
    savecount = mavlink_callback.count

    # Disarm. A callback of None should not throw errors
    v.armed = False
    # NOTE wait crudely for ACK on mode update
    time.sleep(3)

    # Expect the callback to have been called
    assert savecount == mavlink_callback.count

    # Re-arm should not throw errors.
    v.armed = True
    # NOTE wait crudely for ACK on mode update
    time.sleep(3)
