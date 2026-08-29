from dronekit import SystemStatus


def test_state(vehicle):
    assert type(vehicle.system_status) is SystemStatus
    assert type(vehicle.system_status.state) is str
