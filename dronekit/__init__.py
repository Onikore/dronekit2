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

from collections.abc import MutableMapping

import copy
import logging
import math
import struct
import time

from pymavlink import mavutil, mavwp
from pymavlink.dialects.v10 import ardupilotmega

from dronekit.util import ErrprinterHandler

__version__ = "3.0.0.dev0"


from dronekit.errors import APIException, TimeoutError


from dronekit.types import (
    Attitude,
    Battery,
    Capabilities,
    GPSInfo,
    LocationGlobal,
    LocationGlobalRelative,
    LocationLocal,
    Rangefinder,
    SystemStatus,
    VehicleMode,
    Version,
    Wind,
)


from dronekit.observers import HasObservers


from dronekit.channels import Channels, ChannelsOverride


from dronekit.locations import Locations


from dronekit.vehicle import Vehicle, default_still_waiting_callback


from dronekit.gimbal import Gimbal


from dronekit.parameters import Parameters


from dronekit.mission import Command, CommandSequence


from dronekit.connect import connect
