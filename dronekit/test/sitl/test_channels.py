import time


def assert_readback(vehicle, values):
    i = 10.0
    while i > 0:
        time.sleep(0.1)
        i -= 0.1
        for k, v in values.items():
            if vehicle.channels[k] != v:
                continue
        break
    if i <= 0:
        raise Exception(f"Did not match in channels readback {values}")


def test_timeout(vehicle):
    # 18, not 8: dronekit reads the modern RC_CHANNELS message (up to 18
    # channels) in preference to the legacy 8-channel RC_CHANNELS_RAW -
    # confirmed against live SITL, which now sends RC_CHANNELS. Overrides
    # stay at 8: RC_CHANNELS_OVERRIDE, the message channels.overrides sends,
    # is fixed at 8 channels in the wire protocol regardless (see
    # dronekit/channels.py's ChannelsOverride - "Fixed by MAVLink").
    assert len(vehicle.channels) == 18
    assert len(vehicle.channels.overrides) == 8

    # sorted() on strings orders "10" before "2" lexicographically, so sort
    # both sides identically instead of comparing to a numeric range.
    assert sorted(vehicle.channels.keys()) == sorted(str(x) for x in range(1, 19))
    assert sorted(vehicle.channels.overrides.keys()) == []

    assert type(vehicle.channels["1"]) is int
    assert type(vehicle.channels["2"]) is int
    assert type(vehicle.channels["3"]) is int
    assert type(vehicle.channels["4"]) is int
    assert type(vehicle.channels["5"]) is int
    assert type(vehicle.channels["6"]) is int
    assert type(vehicle.channels["7"]) is int
    assert type(vehicle.channels["8"]) is int
    assert type(vehicle.channels[1]) is int
    assert type(vehicle.channels[2]) is int
    assert type(vehicle.channels[3]) is int
    assert type(vehicle.channels[4]) is int
    assert type(vehicle.channels[5]) is int
    assert type(vehicle.channels[6]) is int
    assert type(vehicle.channels[7]) is int
    assert type(vehicle.channels[8]) is int

    vehicle.channels.overrides = {"1": 1010}
    assert_readback(vehicle, {"1": 1010})

    vehicle.channels.overrides = {"2": 1020}
    assert_readback(vehicle, {"1": 1500, "2": 1010})

    vehicle.channels.overrides["1"] = 1010
    assert_readback(vehicle, {"1": 1010, "2": 1020})

    del vehicle.channels.overrides["1"]
    assert_readback(vehicle, {"1": 1500, "2": 1020})

    vehicle.channels.overrides = {"1": 1010, "2": None}
    assert_readback(vehicle, {"1": 1010, "2": 1500})

    vehicle.channels.overrides["1"] = None
    assert_readback(vehicle, {"1": 1500, "2": 1500})

    # test
    try:
        vehicle.channels["19"]
        raise AssertionError("Can read over end of channels")
    except AssertionError:
        raise
    except Exception:
        pass

    try:
        vehicle.channels["0"]
        raise AssertionError("Can read over start of channels")
    except AssertionError:
        raise
    except Exception:
        pass

    try:
        vehicle.channels["1"] = 200
        raise AssertionError("can write a channel value")
    except AssertionError:
        raise
    except Exception:
        pass

    # Set Ch1 to 100 using braces syntax
    vehicle.channels.overrides = {"1": 1000}
    assert_readback(vehicle, {"1": 1000})

    # Set Ch2 to 200 using bracket
    vehicle.channels.overrides["2"] = 200
    assert_readback(vehicle, {"1": 200, "2": 200})

    # Set Ch2 to 1010
    vehicle.channels.overrides = {"2": 1010}
    assert_readback(vehicle, {"1": 1500, "2": 1010})

    # Set Ch3,4,5,6,7 to 300,400-700 respectively
    vehicle.channels.overrides = {"3": 300, "4": 400, "5": 500, "6": 600, "7": 700}
    assert_readback(vehicle, {"3": 300, "4": 400, "5": 500, "6": 600, "7": 700})

    # Set Ch8 to 800 using braces
    vehicle.channels.overrides = {"8": 800}
    assert_readback(vehicle, {"8": 800})

    # Set Ch8 to 800 using brackets
    vehicle.channels.overrides["8"] = 810
    assert_readback(vehicle, {"8": 810})

    try:
        # Try to write channel 9 override to a value with brackets
        vehicle.channels.overrides["9"] = 900
        raise AssertionError("can write channels.overrides 9")
    except AssertionError:
        raise
    except Exception:
        pass

    try:
        # Try to write channel 9 override to a value with braces
        vehicle.channels.overrides = {"9": 900}
        raise AssertionError("can write channels.overrides 9 with braces")
    except AssertionError:
        raise
    except Exception:
        pass

    # Clear channel 3 using brackets
    vehicle.channels.overrides["3"] = None
    assert "3" not in vehicle.channels.overrides, "overrides hould not contain None"

    # Clear channel 2 using braces
    vehicle.channels.overrides = {"2": None}
    assert "2" not in vehicle.channels.overrides, "overrides hould not contain None"

    # Clear all channels
    vehicle.channels.overrides = {}
    assert len(vehicle.channels.overrides.keys()) == 0

    # Set Ch2 to 33, clear channel 6
    vehicle.channels.overrides = {"2": 33, "6": None}
    assert_readback(vehicle, {"2": 33, "6": 1500})
    assert list(vehicle.channels.overrides.keys()) == ["2"]

    # Callbacks
    result = {"success": False}
    vehicle.channels.overrides = {}

    def channels_callback(vehicle, name, channels):
        if channels["3"] == 55:
            result["success"] = True

    vehicle.add_attribute_listener("channels", channels_callback)
    vehicle.channels.overrides = {"3": 55}

    i = 5
    while not result["success"] and i > 0:
        time.sleep(0.1)
        i -= 1
    assert result["success"], "channels callback should be invoked."
