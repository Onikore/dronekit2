import time

from dronekit import connect
from dronekit.mavlink import MAVConnection


def test_mavlink(vehicle):
    out = MAVConnection('udpin:localhost:15668')
    vehicle._handler.pipe(out)
    out.start()

    vehicle2 = connect('udpout:localhost:15668', wait_ready=True)

    try:
        result = {'success': False}

        @vehicle2.on_attribute('location')
        def callback(*args):
            result['success'] = True

        i = 20
        while not result['success'] and i > 0:
            time.sleep(1)
            i -= 1

        assert result['success']
    finally:
        vehicle2.close()
