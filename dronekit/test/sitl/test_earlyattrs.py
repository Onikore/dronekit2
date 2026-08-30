from dronekit import connect


def test_battery_none(sitl_connection_string):
    vehicle = connect(sitl_connection_string, _initialize=False)

    try:
        # Ensure we can get (possibly unpopulated) battery object without throwing error.
        assert vehicle.battery is None

        vehicle.initialize()

        # Ensure we can get battery object without throwing error.
        vehicle.wait_ready("battery")
        assert vehicle.battery is not None
    finally:
        vehicle.close()
