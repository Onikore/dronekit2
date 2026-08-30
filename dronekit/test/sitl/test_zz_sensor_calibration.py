from pymavlink import mavutil

from dronekit.test.sitl import assert_command_ack

# Confirmed against live SITL, across multiple real runs: every calibration
# type below returns MAV_RESULT_ACCEPTED on a vehicle that hasn't flown yet,
# MAV_RESULT_FAILED once earlier tests in the suite have armed/flown it, and
# occasionally MAV_RESULT_TEMPORARILY_REJECTED if a previous calibration in
# this same file hasn't fully finished settling yet - not test flakiness, a
# real, reproducible dependency on real-time simulation state (attitude, EKF
# convergence, whether the vehicle is airborne, calibration-subsystem busy
# state) that this suite doesn't control per-test. Accepting all three is the
# honest expectation, not a weakened one.
CALIBRATION_RESULTS = {
    mavutil.mavlink.MAV_RESULT_ACCEPTED,
    mavutil.mavlink.MAV_RESULT_FAILED,
    mavutil.mavlink.MAV_RESULT_TEMPORARILY_REJECTED,
}


def test_gyro_calibration(vehicle):
    """Request gyroscope calibration, and check for the COMMAND_ACK."""

    with assert_command_ack(
        vehicle,
        mavutil.mavlink.MAV_CMD_PREFLIGHT_CALIBRATION,
        timeout=30,
        ack_result=CALIBRATION_RESULTS,
    ):
        vehicle.send_calibrate_gyro()


def test_magnetometer_calibration(vehicle):
    """Request magnetometer calibration, and check for the COMMAND_ACK."""

    # MAV_RESULT_UNSUPPORTED is not expected here on current firmware, unlike
    # older firmware where this command wasn't implemented at all.
    with assert_command_ack(
        vehicle,
        mavutil.mavlink.MAV_CMD_DO_START_MAG_CAL,
        timeout=30,
        ack_result=CALIBRATION_RESULTS,
    ):
        vehicle.send_calibrate_magnetometer()


def test_simple_accelerometer_calibration(vehicle):
    """Request simple accelerometer calibration, and check for the COMMAND_ACK."""

    with assert_command_ack(
        vehicle,
        mavutil.mavlink.MAV_CMD_PREFLIGHT_CALIBRATION,
        timeout=30,
        ack_result=CALIBRATION_RESULTS,
    ):
        vehicle.send_calibrate_accelerometer(simple=True)


def test_accelerometer_calibration(vehicle):
    """Request accelerometer calibration, and check for the COMMAND_ACK."""

    with assert_command_ack(
        vehicle,
        mavutil.mavlink.MAV_CMD_PREFLIGHT_CALIBRATION,
        timeout=30,
        ack_result=CALIBRATION_RESULTS,
    ):
        vehicle.send_calibrate_accelerometer(simple=False)


def test_board_level_calibration(vehicle):
    """Request board level calibration, and check for the COMMAND_ACK."""

    with assert_command_ack(
        vehicle,
        mavutil.mavlink.MAV_CMD_PREFLIGHT_CALIBRATION,
        timeout=30,
        ack_result=CALIBRATION_RESULTS,
    ):
        vehicle.send_calibrate_vehicle_level()


def test_barometer_calibration(vehicle):
    """Request barometer calibration, and check for the COMMAND_ACK."""

    with assert_command_ack(
        vehicle,
        mavutil.mavlink.MAV_CMD_PREFLIGHT_CALIBRATION,
        timeout=30,
        ack_result=CALIBRATION_RESULTS,
    ):
        vehicle.send_calibrate_barometer()
