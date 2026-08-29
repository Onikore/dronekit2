import time


def current_milli_time():
    return int(round(time.time() * 1000))


def test_timeout(vehicle):
    v = vehicle

    # THR_MIN was renamed to MOT_SPIN_MIN in ArduCopter 3.5+; THR_MIN no
    # longer exists on current firmware.
    value = v.parameters['MOT_SPIN_MIN']
    assert type(value) == float

    # MOT_SPIN_MIN is a 0.0-1.0 fraction, so the delta must stay in range.
    delta = 0.01 if value < 0.5 else -0.01

    start = current_milli_time()
    v.parameters['MOT_SPIN_MIN'] = value + delta
    end = current_milli_time()

    newvalue = v.parameters['MOT_SPIN_MIN']
    assert type(newvalue) == float
    assert abs(newvalue - (value + delta)) < 1e-6

    # Checks that time to set parameter was <1s
    # see https://github.com/dronekit/dronekit-python/issues/12
    assert end - start < 1000, 'time to set parameter was %s, over 1s' % (end - start, )
