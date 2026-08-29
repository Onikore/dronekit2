"""
Simple test to trigger a bug in Vehicle class: issue #610 fixed in PR #611
"""


def test_timeout(vehicle):
    v = vehicle

    # Set the vehicle and autopilot type to 'unsupported' types that MissionPlanner uses as of 17.Apr.2016
    v._vehicle_type = 6
    v._autopilot_type = 8

    # The above types trigger 'TypeError: argument of type 'NoneType' is not iterable' which is addressed in issue #610
    v._is_mode_available(0)
