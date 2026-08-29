import time


def current_milli_time():
    return int(round(time.time() * 1000))


def test_timeout(vehicle):
    v = vehicle

    value = v.parameters['THR_MIN']
    assert type(value) == float

    start = current_milli_time()
    v.parameters['THR_MIN'] = value + 10
    end = current_milli_time()

    newvalue = v.parameters['THR_MIN']
    assert type(newvalue) == float
    assert newvalue == value + 10

    # Checks that time to set parameter was <1s
    # see https://github.com/dronekit/dronekit-python/issues/12
    assert end - start < 1000, 'time to set parameter was %s, over 1s' % (end - start, )
