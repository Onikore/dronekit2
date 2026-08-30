"""Tests for task E7: dronekit.mission.CommandInt (the MISSION_ITEM_INT / int32 x 1e7
mission-item variant), added alongside the existing float32 Command/MISSION_ITEM.

Covers:
  * constructing a CommandInt directly (same constructor shape as Command's underlying
    pymavlink message class - see mission.py's CommandInt docstring),
  * CommandInt.from_command(), the opt-in Command -> CommandInt conversion helper,
  * an empirical, CI-enforced demonstration of the float32 vs int32 x 1e7 precision
    difference, encoded through the *real* MAVLink wire pack/decode path (not just a
    bare struct.pack call) so this keeps testing the actual wire format,
  * that pymavlink's mavwp.MAVWPLoader (what Vehicle._wploader actually is) accepts
    Command and CommandInt objects interchangeably via its generic, message-class-agnostic
    .add()/.count()/.wp()/.set() methods,
  * that Vehicle's mission-download listener (extended in this task to also listen for
    'MISSION_ITEM_INT') correctly decodes a MISSION_ITEM_INT's int32 x/y into degrees
    for the seq-0 home-location special case, and stores mixed MISSION_ITEM /
    MISSION_ITEM_INT messages in the same _wploader without issue.
"""

import io

import pytest
from pymavlink import mavutil, mavwp

from dronekit import Vehicle
from dronekit.mavlink import MAVConnection
from dronekit.mission import Command, CommandInt

# The exact coordinate already used in Command's own docstring example, so the two
# classes' docstrings and this test all refer to the same real-world numbers.
LAT = -34.364114
LON = 149.166022
ALT = 30


def _wire_roundtrip(msg):
    """Pack `msg` exactly as it would go out over the wire, then decode those bytes
    back with a fresh MAVLink parser. This exercises the real pymavlink field
    (de)serialization - float32 for MISSION_ITEM's x/y, int32 for MISSION_ITEM_INT's -
    rather than re-implementing the encoding with a standalone struct.pack call.
    """
    encoder = mavutil.mavlink.MAVLink(io.BytesIO(), srcSystem=1, srcComponent=1)
    encoder.robust_parsing = True
    packed = msg.pack(encoder)

    decoder = mavutil.mavlink.MAVLink(io.BytesIO(), srcSystem=1, srcComponent=1)
    decoder.robust_parsing = True
    decoded = None
    for byte in packed:
        decoded = decoder.parse_char(bytes([byte]))
        if decoded is not None:
            break
    assert decoded is not None, "wire round-trip failed to decode a full message"
    return decoded


# ---------------------------------------------------------------------------
# Constructing CommandInt directly
# ---------------------------------------------------------------------------


def test_command_int_constructs_directly():
    x_int = int(round(LAT * 1e7))
    y_int = int(round(LON * 1e7))
    cmd = CommandInt(
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
        x_int,
        y_int,
        ALT,
    )
    assert cmd.get_type() == "MISSION_ITEM_INT"
    assert cmd.x == x_int
    assert cmd.y == y_int
    assert cmd.z == ALT
    assert cmd.command == mavutil.mavlink.MAV_CMD_NAV_WAYPOINT
    # CommandInt is a real MAVLink message subclass, same as Command.
    assert isinstance(cmd, mavutil.mavlink.MAVLink_mission_item_int_message)


def test_command_int_is_additive_not_a_replacement_for_command():
    """Command (float32 MISSION_ITEM) must stay the default, unaffected class."""
    cmd = Command(
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
        LAT,
        LON,
        ALT,
    )
    assert cmd.get_type() == "MISSION_ITEM"
    assert cmd.x == LAT
    assert cmd.y == LON
    assert not isinstance(cmd, CommandInt)


# ---------------------------------------------------------------------------
# CommandInt.from_command() conversion helper
# ---------------------------------------------------------------------------


def test_from_command_scales_x_y_by_1e7_and_preserves_other_fields():
    cmd = Command(
        7,
        1,
        3,
        mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
        mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,
        1,
        1,
        11,
        22,
        33,
        44,
        LAT,
        LON,
        ALT,
    )
    cmd_int = CommandInt.from_command(cmd)

    assert isinstance(cmd_int, CommandInt)
    assert cmd_int.get_type() == "MISSION_ITEM_INT"
    # Non-location fields pass through unchanged.
    assert cmd_int.target_system == cmd.target_system
    assert cmd_int.target_component == cmd.target_component
    assert cmd_int.seq == cmd.seq
    assert cmd_int.frame == cmd.frame
    assert cmd_int.command == cmd.command
    assert cmd_int.current == cmd.current
    assert cmd_int.autocontinue == cmd.autocontinue
    assert cmd_int.param1 == cmd.param1
    assert cmd_int.param2 == cmd.param2
    assert cmd_int.param3 == cmd.param3
    assert cmd_int.param4 == cmd.param4
    assert cmd_int.z == cmd.z  # altitude is a float in both message types
    # x/y are rescaled to int32 degrees * 1e7.
    assert cmd_int.x == int(round(LAT * 1e7))
    assert cmd_int.y == int(round(LON * 1e7))
    assert cmd_int.x == -343641140
    assert cmd_int.y == 1491660220


# ---------------------------------------------------------------------------
# Precision-loss demonstration: float32 (Command/MISSION_ITEM) vs int32 x 1e7
# (CommandInt/MISSION_ITEM_INT), both encoded/decoded through the real MAVLink
# wire (de)serialization.
# ---------------------------------------------------------------------------

# WGS84-ish equatorial circumference, used only to turn a degree error into an
# approximate ground-distance error for readable assertions/messages.
METRES_PER_DEGREE = 40075017.0 / 360.0


def test_float32_mission_item_loses_precision_on_the_wire():
    cmd = Command(
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
        LAT,
        LON,
        ALT,
    )
    decoded = _wire_roundtrip(cmd)

    # These are the *actual* float32 wire values pymavlink produces for LAT/LON -
    # not restated from a docstring, but the literal decoded result.
    assert decoded.x == pytest.approx(-34.364112854003906, abs=0)
    assert decoded.y == pytest.approx(149.166015625, abs=0)

    lat_err_m = abs(decoded.x - LAT) * METRES_PER_DEGREE
    lon_err_m = abs(decoded.y - LON) * METRES_PER_DEGREE

    # Real, nonzero precision loss: ~12.8cm on latitude, ~71.0cm on longitude for
    # this coordinate (computed, not assumed - see module docstring / mission.py's
    # CommandInt docstring for the same numbers).
    assert lat_err_m > 0.01
    assert lon_err_m > 0.01


def test_int32_mission_item_int_is_exact_on_the_wire():
    cmd_int = CommandInt.from_command(
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
            LAT,
            LON,
            ALT,
        )
    )
    decoded = _wire_roundtrip(cmd_int)

    # No mantissa rounding at all: the int32 the wire carries decodes back to
    # exactly the value that was encoded.
    assert decoded.x == int(round(LAT * 1e7))
    assert decoded.y == int(round(LON * 1e7))
    assert decoded.x / 1e7 == LAT
    assert decoded.y / 1e7 == LON


def test_int32_wire_precision_beats_float32_wire_precision_for_the_same_coordinate():
    """The headline claim of this task, made empirically verifiable: for a real
    coordinate, the int32 x 1e7 encoding preserves strictly more precision than the
    float32 encoding of the same value, over the real MAVLink wire format."""
    cmd = Command(
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
        LAT,
        LON,
        ALT,
    )
    cmd_int = CommandInt.from_command(cmd)

    float_decoded = _wire_roundtrip(cmd)
    int_decoded = _wire_roundtrip(cmd_int)

    float_lat_err = abs(float_decoded.x - LAT)
    float_lon_err = abs(float_decoded.y - LON)
    int_lat_err = abs(int_decoded.x / 1e7 - LAT)
    int_lon_err = abs(int_decoded.y / 1e7 - LON)

    assert int_lat_err == 0.0
    assert int_lon_err == 0.0
    assert float_lat_err > int_lat_err
    assert float_lon_err > int_lon_err

    # The fixed resolution of one int32 unit (1e-7 degree) is ~1.11cm at the
    # equator - real number, computed here, not restated from any prior claim.
    one_unit_m = 1e-7 * METRES_PER_DEGREE
    assert one_unit_m == pytest.approx(0.011132, abs=1e-6)


# ---------------------------------------------------------------------------
# mavwp.MAVWPLoader (what Vehicle._wploader actually is) accepts Command and
# CommandInt interchangeably - no changes needed to the loader itself.
# ---------------------------------------------------------------------------


def test_bare_mavwp_loader_accepts_command_and_command_int_interchangeably():
    loader = mavwp.MAVWPLoader()

    cmd = Command(
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
        LAT,
        LON,
        ALT,
    )
    cmd_int = CommandInt.from_command(cmd)

    assert loader.count() == 0
    loader.add(cmd)
    assert loader.count() == 1
    loader.add(cmd_int)
    assert loader.count() == 2

    item0 = loader.wp(0)
    item1 = loader.wp(1)
    assert item0.get_type() == "MISSION_ITEM"
    assert item1.get_type() == "MISSION_ITEM_INT"
    # .add() stamps .seq for us, keyed purely by position - agnostic to message class.
    assert item0.seq == 0
    assert item1.seq == 1

    # .set() (used by CommandSequence.__setitem__) is equally agnostic.
    replacement = CommandInt.from_command(
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
            1.0,
            2.0,
            3,
        )
    )
    loader.set(replacement, 0)
    assert loader.wp(0).get_type() == "MISSION_ITEM_INT"
    assert loader.wp(0).x == int(round(1.0 * 1e7))


def test_command_sequence_add_accepts_both_via_a_real_vehicle():
    """End-to-end through CommandSequence.add() (not just the bare loader): both
    Command and CommandInt objects can be queued for upload on the same mission."""
    handler = MAVConnection("udpin:127.0.0.1:0")
    try:
        v = Vehicle(handler)
        cmd = Command(
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
            LAT,
            LON,
            ALT,
        )
        cmd_int = CommandInt.from_command(cmd)

        v.commands.add(cmd)
        v.commands.add(cmd_int)

        assert v._wploader.count() == 2
        assert v._wploader.wp(0).get_type() == "MISSION_ITEM"
        assert v._wploader.wp(1).get_type() == "MISSION_ITEM_INT"
    finally:
        handler.master.close()


# ---------------------------------------------------------------------------
# Vehicle's mission-download listener: extended (this task) to also listen for
# 'MISSION_ITEM_INT', and to correctly scale its int32 x/y for the seq-0 home
# location special case.
# ---------------------------------------------------------------------------


class _FakeMissionCountMsg:
    def __init__(self, count):
        self.count = count

    def get_type(self):
        return "MISSION_COUNT"


class _FakeMissionItemMsg:
    """Stands in for a decoded MISSION_ITEM: x/y are plain float degrees."""

    def __init__(self, seq, x=0, y=0, z=0):
        self.seq = seq
        self.x = x
        self.y = y
        self.z = z

    def get_type(self):
        return "MISSION_ITEM"


class _FakeMissionItemIntMsg:
    """Stands in for a decoded MISSION_ITEM_INT: x/y are int32 degrees * 1e7."""

    def __init__(self, seq, x=0, y=0, z=0):
        self.seq = seq
        self.x = x
        self.y = y
        self.z = z

    def get_type(self):
        return "MISSION_ITEM_INT"


@pytest.fixture
def vehicle():
    handler = MAVConnection("udpin:127.0.0.1:0")
    v = Vehicle(handler)
    try:
        yield v
    finally:
        handler.master.close()


def test_download_listener_accepts_mission_item_int(vehicle):
    """MISSION_ITEM_INT must now be a recognized name for the download listener
    (previously only 'WAYPOINT'/'MISSION_ITEM' were), and downloads consisting
    entirely of MISSION_ITEM_INT messages must complete normally."""
    vehicle.commands.download()
    assert vehicle._wp_download_in_progress is True

    vehicle.notify_message_listeners("MISSION_COUNT", _FakeMissionCountMsg(2))
    vehicle.notify_message_listeners(
        "MISSION_ITEM_INT", _FakeMissionItemIntMsg(0, x=int(round(LAT * 1e7)), y=int(round(LON * 1e7)), z=0)
    )
    vehicle.notify_message_listeners(
        "MISSION_ITEM_INT",
        _FakeMissionItemIntMsg(1, x=int(round((LAT + 1) * 1e7)), y=int(round((LON + 1) * 1e7)), z=ALT),
    )

    assert vehicle._wp_download_in_progress is False
    assert vehicle._wploader.count() == 2
    assert len(vehicle.commands) == 1  # count() - 1 for home


def test_download_listener_scales_mission_item_int_home_location_by_1e7(vehicle):
    """Regression test for the int32-vs-float32 home-location bug this task's
    listener change had to account for: a MISSION_ITEM_INT's x/y are raw int32
    (degrees * 1e7), so naively doing LocationGlobal(msg.x, msg.y, msg.z) - which
    is correct for MISSION_ITEM - would store an out-of-range "location" like
    lat=-343641140 for a MISSION_ITEM_INT. The listener must divide by 1e7 first."""
    vehicle.commands.download()

    vehicle.notify_message_listeners("MISSION_COUNT", _FakeMissionCountMsg(1))
    vehicle.notify_message_listeners(
        "MISSION_ITEM_INT",
        _FakeMissionItemIntMsg(0, x=int(round(LAT * 1e7)), y=int(round(LON * 1e7)), z=0),
    )

    home = vehicle._home_location
    assert home is not None
    assert home.lat == pytest.approx(LAT)
    assert home.lon == pytest.approx(LON)


def test_download_listener_accepts_mixed_mission_item_and_mission_item_int(vehicle):
    """A download can freely mix MISSION_ITEM and MISSION_ITEM_INT items across
    sequence numbers - fact 4's claim that MAVWPLoader is message-class-agnostic,
    exercised through the real Vehicle listener rather than the bare loader."""
    vehicle.commands.download()

    vehicle.notify_message_listeners("MISSION_COUNT", _FakeMissionCountMsg(3))
    vehicle.notify_message_listeners("MISSION_ITEM", _FakeMissionItemMsg(0, x=LAT, y=LON, z=0))
    vehicle.notify_message_listeners(
        "MISSION_ITEM_INT", _FakeMissionItemIntMsg(1, x=int(round(LAT * 1e7)), y=int(round(LON * 1e7)), z=ALT)
    )
    vehicle.notify_message_listeners("MISSION_ITEM", _FakeMissionItemMsg(2, x=LAT, y=LON, z=ALT))

    assert vehicle._wp_download_in_progress is False
    assert vehicle._wploader.count() == 3
    assert vehicle._wploader.wp(0).get_type() == "MISSION_ITEM"
    assert vehicle._wploader.wp(1).get_type() == "MISSION_ITEM_INT"
    assert vehicle._wploader.wp(2).get_type() == "MISSION_ITEM"
