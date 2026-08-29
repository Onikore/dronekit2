import time

from dronekit import Vehicle, connect


class DummyVehicle(Vehicle):
    def __init__(self, *args):
        super().__init__(*args)

        self.success = False

        def success_fn(self, name, m):
            self.success = True

        self.add_message_listener('HEARTBEAT', success_fn)


def test_timeout(sitl_connection_string):
    v = connect(sitl_connection_string, vehicle_class=DummyVehicle)

    try:
        while not v.success:
            time.sleep(0.1)
    finally:
        v.close()
