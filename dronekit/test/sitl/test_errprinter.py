import logging
import time

from pymavlink import mavutil

from dronekit import connect


def test_115(sitl_connection_string):
    """Provide a custom status_printer function to the Vehicle and check that
    the autopilot messages are correctly logged.
    """

    logging_check = {"ok": False}

    def errprinter_fn(msg):
        # "APM:Copter" was the product's name years ago; current firmware
        # calls itself "ArduCopter" - confirmed against live SITL.
        if isinstance(msg, str) and "ArduCopter" in msg:
            logging_check["ok"] = True

    # The "autopilot" logger defaults to WARNING (Python's usual default),
    # which silently drops the banner's INFO-severity STATUSTEXT messages
    # before status_printer's handler ever sees them - confirmed against
    # live SITL. Vehicle's own docstring documents this exact setLevel()
    # call as how a caller is expected to opt into it.
    autopilotLogger = logging.getLogger("autopilot")
    previous_level = autopilotLogger.level
    autopilotLogger.setLevel(logging.DEBUG)

    vehicle = connect(sitl_connection_string, wait_ready=False, status_printer=errprinter_fn)

    try:
        # The autopilot only sends its version banner on request (via
        # MAV_CMD_DO_SEND_BANNER), not automatically on connect - confirmed
        # against live SITL, so this test has to ask for it explicitly.
        msg = vehicle.message_factory.command_long_encode(
            vehicle._handler.target_system,
            0,
            mavutil.mavlink.MAV_CMD_DO_SEND_BANNER,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
        )
        vehicle.send_mavlink(msg)

        i = 5
        while not logging_check["ok"] and i > 0:
            time.sleep(1)
            i -= 1

        assert logging_check["ok"]
    finally:
        vehicle.close()

        # Cleanup the logger
        autopilotLogger.removeHandler(autopilotLogger.handlers[0])
        autopilotLogger.setLevel(previous_level)
