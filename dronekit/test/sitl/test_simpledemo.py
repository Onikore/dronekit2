"""
This test represents a simple demo for testing.
Feel free to copy and modify at your leisure.
"""

from dronekit import VehicleMode


# This test runs first!
def test_parameter(vehicle):
    v = vehicle

    # Perform a simple parameter check
    assert type(v.parameters['THR_MIN']) == float


# This test runs second. Add as many tests as you like
def test_mode(vehicle):
    v = vehicle

    # Ensure Mode is an instance of VehicleMode
    assert isinstance(v.mode, VehicleMode)
