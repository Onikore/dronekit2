"""Small, dependency-free value/data-holder types used across dronekit.

These classes have no dependency on Vehicle or any other dronekit
sub-object; they are plain data containers (locations, attitude, GPS
info, version/capabilities info, mode/status wrappers, etc).
"""

from __future__ import annotations

import math

from pymavlink import mavutil


class Attitude:
    """
    Attitude information.

    An object of this type is returned by :py:attr:`Vehicle.attitude`.

    .. _figure_attitude:

    .. figure:: http://upload.wikimedia.org/wikipedia/commons/thumb/c/c1/Yaw_Axis_Corrected.svg/500px-Yaw_Axis_Corrected.svg.png
        :width: 400px
        :alt: Diagram showing Pitch, Roll, Yaw
        :target: http://commons.wikimedia.org/wiki/File:Yaw_Axis_Corrected.svg

        Diagram showing Pitch, Roll, Yaw (`Creative Commons <http://commons.wikimedia.org/wiki/File:Yaw_Axis_Corrected.svg>`_)

    :param pitch: Pitch in radians
    :param yaw: Yaw in radians
    :param roll: Roll in radians
    """

    def __init__(self, pitch: float | None, yaw: float | None, roll: float | None) -> None:
        self.pitch = pitch
        self.yaw = yaw
        self.roll = roll

    def __str__(self) -> str:
        fmt = '{}:pitch={pitch},yaw={yaw},roll={roll}'
        return fmt.format(self.__class__.__name__, **vars(self))


class LocationGlobal:
    """
    A global location object.

    The latitude and longitude are relative to the `WGS84 coordinate system <http://en.wikipedia.org/wiki/World_Geodetic_System>`_.
    The altitude is relative to mean sea-level (MSL).

    For example, a global location object with altitude 30 metres above sea level might be defined as:

    .. code:: python

       LocationGlobal(-34.364114, 149.166022, 30)

    .. todo:: FIXME: Location class - possibly add a vector3 representation.

    An object of this type is owned by :py:attr:`Vehicle.location`. See that class for information on
    reading and observing location in the global frame.

    :param lat: Latitude.
    :param lon: Longitude.
    :param alt: Altitude in meters relative to mean sea-level (MSL).
    """

    def __init__(self, lat: float | None, lon: float | None, alt: float | None = None) -> None:
        self.lat = lat
        self.lon = lon
        self.alt = alt

        # This is for backward compatibility.
        self.local_frame = None
        self.global_frame = None

    def __str__(self) -> str:
        return f"LocationGlobal:lat={self.lat},lon={self.lon},alt={self.alt}"


class LocationGlobalRelative:
    """
    A global location object, with attitude relative to home location altitude.

    The latitude and longitude are relative to the `WGS84 coordinate system <http://en.wikipedia.org/wiki/World_Geodetic_System>`_.
    The altitude is relative to the *home position*.

    For example, a ``LocationGlobalRelative`` object with an altitude of 30 metres above the home location
    might be defined as:

    .. code:: python

       LocationGlobalRelative(-34.364114, 149.166022, 30)

    .. todo:: FIXME: Location class - possibly add a vector3 representation.

    An object of this type is owned by :py:attr:`Vehicle.location`. See that class for information on
    reading and observing location in the global-relative frame.

    :param lat: Latitude.
    :param lon: Longitude.
    :param alt: Altitude in meters (relative to the home location).
    """

    def __init__(self, lat: float | None, lon: float | None, alt: float | None = None) -> None:
        self.lat = lat
        self.lon = lon
        self.alt = alt

        # This is for backward compatibility.
        self.local_frame = None
        self.global_frame = None

    def __str__(self) -> str:
        return f"LocationGlobalRelative:lat={self.lat},lon={self.lon},alt={self.alt}"


class LocationLocal:
    """
    A local location object.

    The north, east and down are relative to the EKF origin.  This is most likely the location where the
    vehicle was turned on.

    An object of this type is owned by :py:attr:`Vehicle.location`. See that class for information on
    reading and observing location in the local frame.

    :param north: Position north of the EKF origin in meters.
    :param east: Position east of the EKF origin in meters.
    :param down: Position down from the EKF origin in meters. (i.e. negative altitude in meters)
    """

    def __init__(self, north: float | None, east: float | None, down: float | None) -> None:
        self.north = north
        self.east = east
        self.down = down

    def __str__(self) -> str:
        return f"LocationLocal:north={self.north},east={self.east},down={self.down}"

    def distance_home(self) -> float | None:
        """
        Distance away from home, in meters. Returns 3D distance if `down` is known, otherwise 2D distance.
        """

        if self.north is not None and self.east is not None:
            if self.down is not None:
                return math.sqrt(self.north**2 + self.east**2 + self.down**2)
            else:
                return math.sqrt(self.north**2 + self.east**2)
        return None


class GPSInfo:
    """
    Standard information about GPS.

    If there is no GPS lock the parameters are set to ``None``.

    :param Int eph: GPS horizontal dilution of position (HDOP).
    :param Int epv: GPS vertical dilution of position (VDOP).
    :param Int fix_type: 0-1: no fix, 2: 2D fix, 3: 3D fix
    :param Int satellites_visible: Number of satellites visible.

    .. todo:: FIXME: GPSInfo class - possibly normalize eph/epv?  report fix type as string?
    """

    def __init__(self, eph: float | None, epv: float | None, fix_type: int | None,
                 satellites_visible: int | None) -> None:
        self.eph = eph
        self.epv = epv
        self.fix_type = fix_type
        self.satellites_visible = satellites_visible

    def __str__(self) -> str:
        return f"GPSInfo:fix={self.fix_type},num_sat={self.satellites_visible}"


class Wind:
    """
    Wind information

    An object of this type is returned by :py:attr: `Vehicle.wind`.

    :param wind_direction: Wind direction in degrees
    :param wind_speed: Wind speed in m/s
    :param wind_speed_z: vertical wind speed in m/s
    """
    def __init__(self, wind_direction: float, wind_speed: float, wind_speed_z: float) -> None:
        self.wind_direction = wind_direction
        self.wind_speed = wind_speed
        self.wind_speed_z = wind_speed_z

    def __str__(self) -> str:
        return (f"Wind: wind direction: {self.wind_direction}, wind speed: {self.wind_speed}, "
                f"wind speed z: {self.wind_speed_z}")


class Battery:
    """
    System battery information.

    An object of this type is returned by :py:attr:`Vehicle.battery`.

    :param voltage: Battery voltage in millivolts.
    :param current: Battery current, in 10 * milliamperes. ``None`` if the autopilot does not support
        current measurement.
    :param level: Remaining battery energy. ``None`` if the autopilot cannot estimate the remaining battery.
    """

    def __init__(self, voltage: float, current: float, level: float) -> None:
        self.voltage = voltage / 1000.0
        if current == -1:
            self.current = None
        else:
            self.current = current / 100.0
        if level == -1:
            self.level = None
        else:
            self.level = level

    def __str__(self) -> str:
        return f"Battery:voltage={self.voltage},current={self.current},level={self.level}"


class Rangefinder:
    """
    Rangefinder readings.

    An object of this type is returned by :py:attr:`Vehicle.rangefinder`.

    :param distance: Distance (metres). ``None`` if the vehicle doesn't have a rangefinder.
    :param voltage: Voltage (volts). ``None`` if the vehicle doesn't have a rangefinder.
    """

    def __init__(self, distance: float | None, voltage: float | None) -> None:
        self.distance = distance
        self.voltage = voltage

    def __str__(self) -> str:
        return f"Rangefinder: distance={self.distance}, voltage={self.voltage}"


class Version:
    """
    Autopilot version and type.

    An object of this type is returned by :py:attr:`Vehicle.version`.

    The version number can be read in a few different formats. To get it in a human-readable
    format, just print `vehicle.version`.  This might print something like "APM:Copter-3.3.2-rc4".

    .. versionadded:: 2.0.3

    .. py:attribute:: major

        Major version number (integer).

    .. py:attribute::minor

        Minor version number (integer).

    .. py:attribute:: patch

        Patch version number (integer).

    .. py:attribute:: release

        Release type (integer). See the enum `FIRMWARE_VERSION_TYPE <http://mavlink.org/messages/common#http://mavlink.org/messages/common#FIRMWARE_VERSION_TYPE_DEV>`_.

        This is a composite of the product release cycle stage (rc, beta etc) and the version in that cycle - e.g. 23.

    """
    def __init__(self, raw_version: int | None, autopilot_type: int | None, vehicle_type: int | None) -> None:
        self.autopilot_type = autopilot_type
        self.vehicle_type = vehicle_type
        self.raw_version = raw_version
        if raw_version is None:
            self.major = None
            self.minor = None
            self.patch = None
            self.release = None
        else:
            self.major   = raw_version >> 24 & 0xFF
            self.minor   = raw_version >> 16 & 0xFF
            self.patch   = raw_version >> 8  & 0xFF
            self.release = raw_version & 0xFF

    def is_stable(self) -> bool:
        """
        Returns True if the autopilot reports that the current firmware is a stable
        release (not a pre-release or development version).
        """
        return self.release == 255

    def release_version(self) -> int | None:
        """
        Returns the version within the release type (an integer).
        This method returns "23" for Copter-3.3rc23.
        """
        if self.release is None:
            return None
        if self.release == 255:
            return 0
        return self.release % 64

    def release_type(self) -> str | None:
        """
        Returns text describing the release type e.g. "alpha", "stable" etc.
        """
        if self.release is None:
            return None
        types = ["dev", "alpha", "beta", "rc"]
        return types[self.release >> 6]

    def __str__(self) -> str:
        prefix = ""

        if self.autopilot_type == mavutil.mavlink.MAV_AUTOPILOT_ARDUPILOTMEGA:
            prefix += "APM:"
        elif self.autopilot_type == mavutil.mavlink.MAV_AUTOPILOT_PX4:
            prefix += "PX4"
        else:
            prefix += "UnknownAutoPilot"

        if self.vehicle_type == mavutil.mavlink.MAV_TYPE_QUADROTOR:
            prefix += "Copter-"
        elif self.vehicle_type == mavutil.mavlink.MAV_TYPE_FIXED_WING:
            prefix += "Plane-"
        elif self.vehicle_type == mavutil.mavlink.MAV_TYPE_GROUND_ROVER:
            prefix += "Rover-"
        else:
            # Pre-existing gap (not introduced by this typing pass):
            # vehicle_type is int | None (Vehicle constructs a Version
            # with self._vehicle_type, which is None until a HEARTBEAT
            # has been received), and this branch never guarded against
            # that - %d on None would raise TypeError at runtime. Not
            # fixed here per the typing-only scope of this change.
            prefix += f"UnknownVehicleType{self.vehicle_type:d}-"  # type: ignore[str-format]

        if self.release_type() is None:
            release_type = "UnknownReleaseType"
        elif self.is_stable():
            release_type = ""
        else:
            # e.g. "-rc23"
            release_type = "-" + str(self.release_type()) + str(self.release_version())

        return prefix + f"{self.major}.{self.minor}.{self.patch}" + release_type


class Capabilities:
    """
    Autopilot capabilities (supported message types and functionality).

    An object of this type is returned by :py:attr:`Vehicle.capabilities`.

    See the enum
    `MAV_PROTOCOL_CAPABILITY <http://mavlink.org/messages/common#MAV_PROTOCOL_CAPABILITY_MISSION_FLOAT>`_.

    .. versionadded:: 2.0.3


    .. py:attribute:: mission_float

        Autopilot supports MISSION float message type (Boolean).

    .. py:attribute:: param_float

        Autopilot supports the PARAM float message type (Boolean).

    .. py:attribute:: mission_int

        Autopilot supports MISSION_INT scaled integer message type (Boolean).

    .. py:attribute:: command_int

        Autopilot supports COMMAND_INT scaled integer message type (Boolean).

    .. py:attribute:: param_union

        Autopilot supports the PARAM_UNION message type (Boolean).

    .. py:attribute:: ftp

        Autopilot supports ftp for file transfers (Boolean).

    .. py:attribute:: set_attitude_target

        Autopilot supports commanding attitude offboard (Boolean).

    .. py:attribute:: set_attitude_target_local_ned

        Autopilot supports commanding position and velocity targets in local NED frame (Boolean).

    .. py:attribute:: set_altitude_target_global_int

        Autopilot supports commanding position and velocity targets in global scaled integers (Boolean).

    .. py:attribute:: terrain

        Autopilot supports terrain protocol / data handling (Boolean).

    .. py:attribute:: set_actuator_target

        Autopilot supports direct actuator control (Boolean).

    .. py:attribute:: flight_termination

        Autopilot supports the flight termination command (Boolean).

    .. py:attribute:: compass_calibration

        Autopilot supports onboard compass calibration (Boolean).
    """
    def __init__(self, capabilities: int) -> None:
        self.mission_float                  = (((capabilities >> 0)  & 1) == 1)
        self.param_float                    = (((capabilities >> 1)  & 1) == 1)
        self.mission_int                    = (((capabilities >> 2)  & 1) == 1)
        self.command_int                    = (((capabilities >> 3)  & 1) == 1)
        self.param_union                    = (((capabilities >> 4)  & 1) == 1)
        self.ftp                            = (((capabilities >> 5)  & 1) == 1)
        self.set_attitude_target            = (((capabilities >> 6)  & 1) == 1)
        self.set_attitude_target_local_ned  = (((capabilities >> 7)  & 1) == 1)
        self.set_altitude_target_global_int = (((capabilities >> 8)  & 1) == 1)
        self.terrain                        = (((capabilities >> 9)  & 1) == 1)
        self.set_actuator_target            = (((capabilities >> 10) & 1) == 1)
        self.flight_termination             = (((capabilities >> 11) & 1) == 1)
        self.compass_calibration            = (((capabilities >> 12) & 1) == 1)


class VehicleMode:
    """
    This object is used to get and set the current "flight mode".

    The flight mode determines the behaviour of the vehicle and what commands it can obey.
    The recommended flight modes for *DroneKit-Python* apps depend on the vehicle type:

    * Copter apps should use ``AUTO`` mode for "normal" waypoint missions and ``GUIDED`` mode otherwise.
    * Plane and Rover apps should use the ``AUTO`` mode in all cases, re-writing the mission commands if "dynamic"
      behaviour is required (they support only a limited subset of commands in ``GUIDED`` mode).
    * Some modes like ``RETURN_TO_LAUNCH`` can be used on all platforms. Care should be taken
      when using manual modes as these may require remote control input from the user.

    The available set of supported flight modes is vehicle-specific (see
    `Copter Modes <http://copter.ardupilot.com/wiki/flying-arducopter/flight-modes/>`_,
    `Plane Modes <http://plane.ardupilot.com/wiki/flying/flight-modes/>`_,
    `Rover Modes <http://rover.ardupilot.com/wiki/configuration-2/#mode_meanings>`_). If an unsupported mode
    is set the script will raise a ``KeyError`` exception.

    The :py:attr:`Vehicle.mode` attribute can be queried for the current mode.
    The code snippet below shows how to observe changes to the mode and then read the value:

    .. code:: python

        #Callback definition for mode observer
        def mode_callback(self, attr_name):
            print "Vehicle Mode", self.mode

        #Add observer callback for attribute `mode`
        vehicle.add_attribute_listener('mode', mode_callback)

    The code snippet below shows how to change the vehicle mode to AUTO:

    .. code:: python

        # Set the vehicle into auto mode
        vehicle.mode = VehicleMode("AUTO")

    For more information on getting/setting/observing the :py:attr:`Vehicle.mode`
    (and other attributes) see the :ref:`attributes guide <vehicle_state_attributes>`.

    .. py:attribute:: name

        The mode name, as a ``string``.
    """

    def __init__(self, name: str) -> None:
        self.name = name

    def __str__(self) -> str:
        return f"VehicleMode:{self.name}"

    def __eq__(self, other: object) -> bool:
        return self.name == other

    def __ne__(self, other: object) -> bool:
        return self.name != other


class SystemStatus:
    """
    This object is used to get and set the current "system status".

    An object of this type is returned by :py:attr:`Vehicle.system_status`.

    .. py:attribute:: state

        The system state, as a ``string``.
    """

    def __init__(self, state: str) -> None:
        self.state = state

    def __str__(self) -> str:
        return f"SystemStatus:{self.state}"

    def __eq__(self, other: object) -> bool:
        return self.state == other

    def __ne__(self, other: object) -> bool:
        return self.state != other
