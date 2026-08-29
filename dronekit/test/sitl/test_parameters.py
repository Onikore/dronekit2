import time


def test_parameters(vehicle):
    # When called on startup, parameter (may!) be none.
    # assert vehicle.parameters.get('MOT_SPIN_MIN', wait_ready=False) is None

    # With wait_ready, it should not be none.
    assert vehicle.parameters.get('MOT_SPIN_MIN', wait_ready=True) is not None

    try:
        assert vehicle.parameters['MOT_SPIN_MIN'] is not None
    except AssertionError:
        raise
    except Exception as e:
        raise AssertionError() from e

    # Garbage value after all parameters are downloaded should be None.
    assert vehicle.parameters.get('xXx_extreme_garbage_value_xXx', wait_ready=True) is None


def test_iterating(vehicle):
    # Iterate over parameters (testing that iteration works at all - not
    # consuming the values, so the loop variables are intentionally unused).
    for _k, _v in vehicle.parameters.items():
        break
    for _key in vehicle.parameters:
        break


def test_setting(vehicle):
    assert vehicle.parameters['MOT_SPIN_MIN'] is not None

    # 0.20 must stay within MOT_SPIN_MIN's valid 0.0-1.0 range (unlike the
    # THR_MIN parameter this test originally used, which no longer exists
    # on current ArduCopter firmware and had a much wider valid range).
    target = 0.20
    result = {'success': False}

    @vehicle.parameters.on_attribute('MOT_SPIN_MIN')
    def listener(self, name, value):
        result['success'] = (name == 'MOT_SPIN_MIN' and abs(value - target) < 1e-6)

    vehicle.parameters['MOT_SPIN_MIN'] = target

    # Wait a bit.
    i = 5
    while not result['success'] and i > 0:
        time.sleep(1)
        i = i - 1

    assert result['success']
