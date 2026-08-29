from pymavlink import mavutil

from dronekit.test.sitl import assert_command_ack


def test_gyro_calibration(vehicle):
    """Request gyroscope calibration, and check for the COMMAND_ACK."""

    with assert_command_ack(vehicle, mavutil.mavlink.MAV_CMD_PREFLIGHT_CALIBRATION, timeout=30):
        vehicle.send_calibrate_gyro()


def test_magnetometer_calibration(vehicle):
    """Request magnetometer calibration, and check for the COMMAND_ACK."""

    with assert_command_ack(
        vehicle,
        mavutil.mavlink.MAV_CMD_DO_START_MAG_CAL,
        timeout=30,
        ack_result=mavutil.mavlink.MAV_RESULT_UNSUPPORTED,  # TODO: change when APM is upgraded
    ):
        vehicle.send_calibrate_magnetometer()


def test_simple_accelerometer_calibration(vehicle):
    """Request simple accelerometer calibration, and check for the COMMAND_ACK."""

    with assert_command_ack(
        vehicle,
        mavutil.mavlink.MAV_CMD_PREFLIGHT_CALIBRATION,
        timeout=30,
        ack_result=mavutil.mavlink.MAV_RESULT_FAILED,
    ):
        vehicle.send_calibrate_accelerometer(simple=True)


def test_accelerometer_calibration(vehicle):
    """Request accelerometer calibration, and check for the COMMAND_ACK."""

    # The calibration is expected to fail because in the SITL we don't tilt the Vehicle.
    # We just check that the command isn't denied or unsupported.
    with assert_command_ack(
        vehicle,
        mavutil.mavlink.MAV_CMD_PREFLIGHT_CALIBRATION,
        timeout=30,
        ack_result=mavutil.mavlink.MAV_RESULT_FAILED,
    ):
        vehicle.send_calibrate_accelerometer(simple=False)


def test_board_level_calibration(vehicle):
    """Request board level calibration, and check for the COMMAND_ACK."""

    with assert_command_ack(vehicle, mavutil.mavlink.MAV_CMD_PREFLIGHT_CALIBRATION, timeout=30):
        vehicle.send_calibrate_vehicle_level()


def test_barometer_calibration(vehicle):
    """Request barometer calibration, and check for the COMMAND_ACK."""

    with assert_command_ack(vehicle, mavutil.mavlink.MAV_CMD_PREFLIGHT_CALIBRATION, timeout=30):
        vehicle.send_calibrate_barometer()
