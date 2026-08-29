import logging
import time

from dronekit import connect


def test_115(sitl_connection_string):
    """Provide a custom status_printer function to the Vehicle and check that
    the autopilot messages are correctly logged.
    """

    logging_check = {'ok': False}

    def errprinter_fn(msg):
        if isinstance(msg, str) and "APM:Copter" in msg:
            logging_check['ok'] = True

    vehicle = connect(sitl_connection_string, wait_ready=False, status_printer=errprinter_fn)

    try:
        i = 5
        while not logging_check['ok'] and i > 0:
            time.sleep(1)
            i -= 1

        assert logging_check['ok']
    finally:
        vehicle.close()

        # Cleanup the logger
        autopilotLogger = logging.getLogger('autopilot')
        autopilotLogger.removeHandler(autopilotLogger.handlers[0])
