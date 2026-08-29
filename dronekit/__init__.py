# DroneAPI module
"""
This is the API Reference for the DroneKit-Python API.

The main API is the :py:class:`Vehicle` class.
The code snippet below shows how to use :py:func:`connect` to obtain an instance of a connected vehicle:

.. code:: python

    from dronekit import connect

    # Connect to the Vehicle using "connection string" (in this case an address on network)
    vehicle = connect('127.0.0.1:14550', wait_ready=True)

:py:class:`Vehicle` provides access to vehicle *state* through python attributes
(e.g. :py:attr:`Vehicle.mode`)
and to settings/parameters though the :py:attr:`Vehicle.parameters` attribute.
Asynchronous notification on vehicle attribute changes is available by registering listeners/observers.

Vehicle movement is primarily controlled using the :py:attr:`Vehicle.armed` attribute and
:py:func:`Vehicle.simple_takeoff` and :py:attr:`Vehicle.simple_goto` in GUIDED mode.

Velocity-based movement and control over other vehicle features can be achieved using custom MAVLink messages
(:py:func:`Vehicle.send_mavlink`, :py:func:`Vehicle.message_factory`).

It is also possible to work with vehicle "missions" using the :py:attr:`Vehicle.commands` attribute, and run them in AUTO mode.

All the logging is handled through the builtin Python `logging` module.

A number of other useful classes and methods are listed below.

----
"""

# dronekit/test/unit/test_vehicle_defects.py monkeypatches `dronekit.time.time`
# to assert that the moved-out modules (vehicle.py, mission.py) measure
# durations with time.monotonic() and never call time.time(). That only
# reaches the shared `time` module object through this package's own
# namespace, so this import needs to stay here even though nothing in this
# facade file itself calls `time` directly.
import time  # noqa: F401 - re-exposed for tests to patch dronekit.time.time

from dronekit.errors import APIException, TimeoutError
from dronekit.types import (
    Attitude,
    LocationGlobal,
    LocationGlobalRelative,
    LocationLocal,
    GPSInfo,
    Wind,
    Battery,
    Rangefinder,
    Version,
    Capabilities,
    VehicleMode,
    SystemStatus,
)
from dronekit.observers import HasObservers
from dronekit.channels import ChannelsOverride, Channels
from dronekit.locations import Locations
from dronekit.vehicle import Vehicle
from dronekit.gimbal import Gimbal
from dronekit.parameters import Parameters
from dronekit.mission import Command, CommandInt, CommandSequence
from dronekit.vehicle import default_still_waiting_callback
from dronekit.connect import connect

__version__ = "3.0.0"

__all__ = [
    "APIException",
    "TimeoutError",
    "Attitude",
    "LocationGlobal",
    "LocationGlobalRelative",
    "LocationLocal",
    "GPSInfo",
    "Wind",
    "Battery",
    "Rangefinder",
    "Version",
    "Capabilities",
    "VehicleMode",
    "SystemStatus",
    "HasObservers",
    "ChannelsOverride",
    "Channels",
    "Locations",
    "Vehicle",
    "Gimbal",
    "Parameters",
    "Command",
    "CommandInt",
    "CommandSequence",
    "default_still_waiting_callback",
    "connect",
]
