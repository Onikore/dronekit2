import time


def test_parameters(vehicle):
    # When called on startup, parameter (may!) be none.
    # assert vehicle.parameters.get('THR_MIN', wait_ready=False) is None

    # With wait_ready, it should not be none.
    assert vehicle.parameters.get('THR_MIN', wait_ready=True) is not None

    try:
        assert vehicle.parameters['THR_MIN'] is not None
    except AssertionError:
        raise
    except Exception:
        assert False

    # Garbage value after all parameters are downloaded should be None.
    assert vehicle.parameters.get('xXx_extreme_garbage_value_xXx', wait_ready=True) is None


def test_iterating(vehicle):
    # Iterate over parameters.
    for k, v in vehicle.parameters.items():
        break
    for key in vehicle.parameters:
        break


def test_setting(vehicle):
    assert vehicle.parameters['THR_MIN'] is not None

    result = {'success': False}

    @vehicle.parameters.on_attribute('THR_MIN')
    def listener(self, name, value):
        result['success'] = (name == 'THR_MIN' and value == 3.000)

    vehicle.parameters['THR_MIN'] = 3.000

    # Wait a bit.
    i = 5
    while not result['success'] and i > 0:
        time.sleep(1)
        i = i - 1

    assert result['success']
