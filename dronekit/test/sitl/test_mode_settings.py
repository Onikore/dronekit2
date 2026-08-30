def test_modes_set(vehicle):
    def listener(self, name, m):
        assert self._flightmode == "STABILIZE"

    vehicle.add_message_listener("HEARTBEAT", listener)
