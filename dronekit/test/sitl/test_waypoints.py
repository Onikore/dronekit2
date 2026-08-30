import time

from pymavlink import mavutil

from dronekit import Command, CommandInt, LocationGlobal


def test_empty_clear(vehicle):
    # Calling clear() on an empty object should not crash.
    # upload()'s timeout defaults to None (block forever) - explicit here
    # since the upload handshake was observed to genuinely hang without one
    # elsewhere in this file, late in the suite.
    vehicle.commands.clear()
    vehicle.commands.upload(timeout=30)

    assert len(vehicle.commands) == 0


def test_set_home(vehicle):
    # Wait for home position to be real and not 0, 0, 0
    # once we request it via cmds.download()
    time.sleep(10)
    vehicle.commands.download()
    vehicle.commands.wait_ready()
    assert vehicle.home_location is not None

    # Note: If the GPS values differ heavily from EKF values, this command
    # will basically fail silently. This GPS coordinate is tailored for the
    # SITL home location used elsewhere in this suite, so it doesn't fail.
    vehicle.home_location = LocationGlobal(-35, 149, 600)
    vehicle.commands.download()
    vehicle.commands.wait_ready()

    assert vehicle.home_location.lat == -35
    assert vehicle.home_location.lon == 149
    assert vehicle.home_location.alt == 600


def test_parameter(vehicle):
    # Home should be None at first.
    assert vehicle.home_location is None

    # Wait for home position to be real and not 0, 0, 0
    # once we request it via cmds.download()
    time.sleep(10)

    # Tests share one persistent SITL process for the whole run, so the
    # mission may already hold commands left over from an earlier test -
    # confirmed against live SITL. Clear it explicitly rather than assume.
    # upload()'s timeout defaults to None (block forever) - explicit here
    # since this late in the suite the upload handshake was observed to
    # genuinely hang without one.
    vehicle.commands.clear()
    vehicle.commands.upload(timeout=30)
    vehicle.commands.download()
    vehicle.commands.wait_ready()
    assert len(vehicle.commands) == 0
    assert vehicle.home_location is not None

    # Save home for comparison.
    home = vehicle.home_location

    # Upload
    # CommandInt (MISSION_ITEM_INT), not Command (legacy float32 MISSION_ITEM):
    # current firmware logs "got MISSION_ITEM; GCS should send MISSION_ITEM_INT"
    # and never completes the upload handshake for the old format - confirmed
    # against live SITL (upload() genuinely never returns without a timeout).
    #
    # MAV_CMD_CONDITION_CHANGE_ALT (113) is no longer supported by current
    # firmware - confirmed against live SITL: the final MISSION_ACK comes
    # back MAV_MISSION_UNSUPPORTED, and in a longer mission the autopilot
    # silently abandons requesting any items after it (which is what made
    # this look like an upload hang, not a rejection). Swapped for another
    # MAV_CMD_NAV_WAYPOINT - CONDITION_YAW (115, elsewhere in this list) is
    # still supported and was left as-is.
    for command in [
        CommandInt.from_command(Command(0, 0, 0, 0, 16, 1, 1, 0.0, 0.0, 0.0, 0.0, -35.3605, 149.172363, 747.0)),
        CommandInt.from_command(Command(0, 0, 0, 3, 22, 0, 1, 0.0, 0.0, 0.0, 0.0, -35.359831, 149.166334, 100.0)),
        CommandInt.from_command(Command(0, 0, 0, 3, 16, 0, 1, 0.0, 0.0, 0.0, 0.0, -35.363489, 149.167213, 100.0)),
        CommandInt.from_command(Command(0, 0, 0, 3, 16, 0, 1, 0.0, 0.0, 0.0, 0.0, -35.355491, 149.169595, 100.0)),
        CommandInt.from_command(Command(0, 0, 0, 3, 16, 0, 1, 0.0, 0.0, 0.0, 0.0, -35.355071, 149.175839, 100.0)),
        CommandInt.from_command(Command(0, 0, 0, 3, 16, 0, 1, 0.0, 0.0, 0.0, 0.0, -35.362666, 149.178715, 100.0)),
        CommandInt.from_command(Command(0, 0, 0, 3, 115, 0, 1, 2.0, 22.0, 1.0, 3.0, 0.0, 0.0, 0.0)),
        CommandInt.from_command(Command(0, 0, 0, 3, 16, 0, 1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)),
    ]:
        vehicle.commands.add(command)
    # upload()'s timeout defaults to None (block forever) - the same
    # observed-hang risk as the clear() upload above, so explicit here too.
    vehicle.commands.upload(timeout=30)

    # After upload
    vehicle.commands.download()
    vehicle.commands.wait_ready()
    assert len(vehicle.commands) == 8

    # Test iteration.
    count = 0
    for cmd in vehicle.commands:
        assert cmd is not None
        count += 1
    assert count == 8

    # Test slicing
    count = 3
    for cmd in vehicle.commands[2:5]:
        assert cmd is not None
        assert cmd.seq == count
        count += 1
    assert count == 6

    # Test next property
    assert vehicle.commands.next == 0
    vehicle.commands.next = 3
    while vehicle.commands.next != 3:
        time.sleep(0.1)
    assert vehicle.commands.next == 3

    # Home should be preserved
    assert home.lat == vehicle.home_location.lat
    assert home.lon == vehicle.home_location.lon
    assert home.alt == vehicle.home_location.alt


def test_227(vehicle):
    """
    Tests race condition when downloading items
    """

    def assert_commands(count):
        vehicle.commands.download()
        vehicle.commands.wait_ready()
        assert len(vehicle.commands) == count

    # Tests share one persistent SITL process for the whole run, so the
    # mission may already hold commands left over from an earlier test -
    # confirmed against live SITL. Clear it explicitly rather than assume.
    # upload()'s timeout defaults to None (block forever) - explicit here
    # since this late in the suite the upload handshake was observed to
    # genuinely hang without one.
    vehicle.commands.clear()
    vehicle.commands.upload(timeout=30)
    assert_commands(0)

    vehicle.commands.add(
        CommandInt.from_command(
            Command(
                0,
                0,
                0,
                mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
                mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,
                0,
                0,
                0,
                0,
                0,
                0,
                10,
                10,
                10,
            )
        )
    )
    # flush() is deprecated sugar for commands.upload(timeout=None) - explicit
    # timeout here for the same reason as the other upload() calls above.
    vehicle.commands.upload(timeout=30)

    assert_commands(1)
