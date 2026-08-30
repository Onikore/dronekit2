"""Unit tests for dronekit's plain value/data-holder types.

These need no live vehicle connection at all - see dronekit/test/conftest.py
for the fixtures that gate the SITL/hardware tests under dronekit/test/sitl.
"""

from dronekit import (
    Attitude,
    Battery,
    GPSInfo,
    LocationGlobal,
    LocationGlobalRelative,
    LocationLocal,
    Rangefinder,
    SystemStatus,
    VehicleMode,
    Version,
    Wind,
)

# ---------------------------------------------------------------------------
# LocationGlobal
# ---------------------------------------------------------------------------


def test_location_global_stores_lat_lon_alt():
    loc = LocationGlobal(-35.363261, 149.165230, 584.0)
    assert loc.lat == -35.363261
    assert loc.lon == 149.165230
    assert loc.alt == 584.0


def test_location_global_alt_defaults_to_none():
    loc = LocationGlobal(-35.363261, 149.165230)
    assert loc.alt is None


def test_location_global_backward_compat_frames_are_none():
    loc = LocationGlobal(1, 2, 3)
    assert loc.local_frame is None
    assert loc.global_frame is None


def test_location_global_str():
    loc = LocationGlobal(1, 2, 3)
    assert str(loc) == "LocationGlobal:lat=1,lon=2,alt=3"


# ---------------------------------------------------------------------------
# LocationGlobalRelative
# ---------------------------------------------------------------------------


def test_location_global_relative_stores_lat_lon_alt():
    loc = LocationGlobalRelative(-35.361354, 149.165218, 20)
    assert loc.lat == -35.361354
    assert loc.lon == 149.165218
    assert loc.alt == 20


def test_location_global_relative_alt_defaults_to_none():
    loc = LocationGlobalRelative(-35.361354, 149.165218)
    assert loc.alt is None


def test_location_global_relative_backward_compat_frames_are_none():
    loc = LocationGlobalRelative(1, 2, 3)
    assert loc.local_frame is None
    assert loc.global_frame is None


def test_location_global_relative_str():
    loc = LocationGlobalRelative(1, 2, 3)
    assert str(loc) == "LocationGlobalRelative:lat=1,lon=2,alt=3"


# ---------------------------------------------------------------------------
# LocationLocal
# ---------------------------------------------------------------------------


def test_location_local_stores_north_east_down():
    loc = LocationLocal(1.0, 2.0, 3.0)
    assert loc.north == 1.0
    assert loc.east == 2.0
    assert loc.down == 3.0


def test_location_local_str():
    loc = LocationLocal(1.0, 2.0, 3.0)
    assert str(loc) == "LocationLocal:north=1.0,east=2.0,down=3.0"


def test_location_local_distance_home_is_3d_when_down_known():
    # 3-4-12-13 extended to 3D: 3^2 + 4^2 + 12^2 == 13^2.
    loc = LocationLocal(3.0, 4.0, 12.0)
    assert loc.distance_home() == 13.0


def test_location_local_distance_home_falls_back_to_2d_when_down_is_none():
    loc = LocationLocal(3.0, 4.0, None)
    assert loc.distance_home() == 5.0


def test_location_local_distance_home_zero_at_origin():
    loc = LocationLocal(0.0, 0.0, 0.0)
    assert loc.distance_home() == 0.0


def test_location_local_distance_home_none_when_north_missing():
    assert LocationLocal(None, 4.0, 12.0).distance_home() is None


def test_location_local_distance_home_none_when_east_missing():
    assert LocationLocal(3.0, None, 12.0).distance_home() is None


def test_location_local_distance_home_none_when_all_missing():
    assert LocationLocal(None, None, None).distance_home() is None


# ---------------------------------------------------------------------------
# Attitude
# ---------------------------------------------------------------------------


def test_attitude_stores_pitch_yaw_roll():
    att = Attitude(0.1, 0.2, 0.3)
    assert att.pitch == 0.1
    assert att.yaw == 0.2
    assert att.roll == 0.3


def test_attitude_str():
    att = Attitude(0.1, 0.2, 0.3)
    assert str(att) == "Attitude:pitch=0.1,yaw=0.2,roll=0.3"


# ---------------------------------------------------------------------------
# Battery
# ---------------------------------------------------------------------------


def test_battery_converts_voltage_from_millivolts():
    batt = Battery(12000, 0, 100)
    assert batt.voltage == 12.0


def test_battery_converts_current_from_centiamps():
    batt = Battery(12000, 250, 100)
    assert batt.current == 2.5


def test_battery_current_is_none_when_unsupported():
    # The autopilot signals "no current sensor" with a raw value of -1.
    batt = Battery(12000, -1, 100)
    assert batt.current is None


def test_battery_level_is_none_when_unsupported():
    # The autopilot signals "can't estimate remaining battery" with -1.
    batt = Battery(12000, 250, -1)
    assert batt.level is None


def test_battery_level_passthrough():
    batt = Battery(12000, 250, 42)
    assert batt.level == 42


def test_battery_str():
    batt = Battery(12000, 250, 42)
    assert str(batt) == "Battery:voltage=12.0,current=2.5,level=42"


# ---------------------------------------------------------------------------
# GPSInfo
# ---------------------------------------------------------------------------


def test_gps_info_stores_fields():
    gps = GPSInfo(1.5, 2.5, 3, 8)
    assert gps.eph == 1.5
    assert gps.epv == 2.5
    assert gps.fix_type == 3
    assert gps.satellites_visible == 8


def test_gps_info_allows_none_when_no_fix():
    gps = GPSInfo(None, None, 0, 0)
    assert gps.eph is None
    assert gps.epv is None
    assert gps.fix_type == 0
    assert gps.satellites_visible == 0


def test_gps_info_str_reports_fix_and_satellite_count():
    gps = GPSInfo(1.5, 2.5, 3, 8)
    assert str(gps) == "GPSInfo:fix=3,num_sat=8"


# ---------------------------------------------------------------------------
# Wind
# ---------------------------------------------------------------------------


def test_wind_stores_fields():
    wind = Wind(180.0, 5.5, -0.2)
    assert wind.wind_direction == 180.0
    assert wind.wind_speed == 5.5
    assert wind.wind_speed_z == -0.2


def test_wind_str():
    wind = Wind(180.0, 5.5, -0.2)
    assert str(wind) == "Wind: wind direction: 180.0, wind speed: 5.5, wind speed z: -0.2"


# ---------------------------------------------------------------------------
# Rangefinder
# ---------------------------------------------------------------------------


def test_rangefinder_stores_fields():
    rf = Rangefinder(1.23, 3.3)
    assert rf.distance == 1.23
    assert rf.voltage == 3.3


def test_rangefinder_allows_none_when_no_sensor():
    # Vehicle.rangefinder documents both fields as None when there's no
    # rangefinder fitted.
    rf = Rangefinder(None, None)
    assert rf.distance is None
    assert rf.voltage is None


def test_rangefinder_str():
    rf = Rangefinder(1.23, 3.3)
    assert str(rf) == "Rangefinder: distance=1.23, voltage=3.3"


# ---------------------------------------------------------------------------
# VehicleMode
# ---------------------------------------------------------------------------


def test_vehicle_mode_equal_same_name():
    assert VehicleMode("GUIDED") == VehicleMode("GUIDED")


def test_vehicle_mode_not_equal_different_name():
    assert VehicleMode("AUTO") != VehicleMode("GUIDED")


def test_vehicle_mode_equal_to_plain_string():
    # Flight scripts routinely compare vehicle.mode directly against a
    # string (e.g. `while vehicle.mode.name != 'GUIDED':`), so VehicleMode's
    # __eq__/__ne__ compare against plain strings too, not just other
    # VehicleMode instances.
    assert VehicleMode("GUIDED") == "GUIDED"
    assert VehicleMode("GUIDED") != "AUTO"


def test_vehicle_mode_str():
    assert str(VehicleMode("LOITER")) == "VehicleMode:LOITER"


# ---------------------------------------------------------------------------
# SystemStatus
# ---------------------------------------------------------------------------


def test_system_status_equal_same_state():
    assert SystemStatus("ACTIVE") == SystemStatus("ACTIVE")


def test_system_status_not_equal_different_state():
    assert SystemStatus("ACTIVE") != SystemStatus("STANDBY")


def test_system_status_equal_to_plain_string():
    assert SystemStatus("ACTIVE") == "ACTIVE"
    assert SystemStatus("ACTIVE") != "STANDBY"


def test_system_status_str():
    assert str(SystemStatus("STANDBY")) == "SystemStatus:STANDBY"


# ---------------------------------------------------------------------------
# Version
# ---------------------------------------------------------------------------


def _make_version(major, minor, patch, release, autopilot_type=3, vehicle_type=2):
    raw_version = (major << 24) | (minor << 16) | (patch << 8) | release
    return Version(raw_version, autopilot_type, vehicle_type)


def test_version_decodes_major_minor_patch_release_from_raw():
    v = _make_version(3, 3, 2, 23)
    assert v.major == 3
    assert v.minor == 3
    assert v.patch == 2
    assert v.release == 23


def test_version_all_fields_none_when_raw_version_is_none():
    # connect() passes raw_version=None until an AUTOPILOT_VERSION message
    # has actually been received.
    v = Version(None, 3, 2)
    assert v.major is None
    assert v.minor is None
    assert v.patch is None
    assert v.release is None
    assert v.is_stable() is False
    assert v.release_version() is None
    assert v.release_type() is None


def test_version_is_stable_true_for_official_release():
    # FIRMWARE_VERSION_TYPE_OFFICIAL == 255.
    v = _make_version(3, 3, 2, 255)
    assert v.is_stable() is True


def test_version_is_stable_false_for_rc():
    # FIRMWARE_VERSION_TYPE_RC starts at 192; 192+23 is "rc23".
    v = _make_version(3, 3, 0, 192 + 23)
    assert v.is_stable() is False


def test_version_release_version_for_rc23():
    # Matches the class docstring's own example: Copter-3.3rc23 should
    # report release_version() == 23.
    v = _make_version(3, 3, 0, 192 + 23)
    assert v.release_version() == 23


def test_version_release_version_is_zero_for_stable():
    v = _make_version(3, 3, 2, 255)
    assert v.release_version() == 0


def test_version_release_type_dev():
    v = _make_version(3, 4, 0, 0)
    assert v.release_type() == "dev"


def test_version_release_type_alpha():
    v = _make_version(3, 4, 0, 64 + 5)
    assert v.release_type() == "alpha"


def test_version_release_type_beta():
    v = _make_version(3, 4, 0, 128 + 10)
    assert v.release_type() == "beta"


def test_version_release_type_rc():
    v = _make_version(3, 4, 0, 192 + 1)
    assert v.release_type() == "rc"


def test_version_release_type_for_stable_release_is_actually_rc():
    # This looks like it should say "stable", but release_type() only
    # inspects the top two bits of `release` (release >> 6), and the
    # official/stable sentinel value happens to be 255 == 0b11111111, whose
    # top two bits alias the same bucket as the "rc" range (0b11xxxxxx). So
    # release_type() returns "rc" even for a stable release - this is the
    # method's real, verified behaviour, not a typo in this test. Use
    # is_stable() to actually detect a stable release.
    v = _make_version(3, 3, 2, 255)
    assert v.release_type() == "rc"


def test_version_str_stable_release_has_no_suffix():
    v = _make_version(3, 3, 2, 255)
    assert str(v) == "APM:Copter-3.3.2"


def test_version_str_rc_release_has_suffix():
    v = _make_version(3, 3, 0, 192 + 23)
    assert str(v) == "APM:Copter-3.3.0-rc23"
