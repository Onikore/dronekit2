"""Mission ("command sequence") waypoint objects for a Vehicle."""

from __future__ import annotations

import time
from typing import Any

from pymavlink import mavutil

from dronekit.errors import APIException, TimeoutError
from dronekit.protocols import VehicleLike


class Command(mavutil.mavlink.MAVLink_mission_item_message):
    """
    A waypoint object.

    This object encodes a single mission item command. The set of commands that are supported
    by ArduPilot in Copter, Plane and Rover (along with their parameters) are listed in the wiki article
    `MAVLink Mission Command Messages (MAV_CMD) <http://planner.ardupilot.com/wiki/common-mavlink-mission-command-messages-mav_cmd/>`_.

    For example, to create a `NAV_WAYPOINT <http://planner.ardupilot.com/wiki/common-mavlink-mission-command-messages-mav_cmd/#mav_cmd_nav_waypoint>`_ command:

    .. code:: python

        cmd = Command(0,0,0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
            mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0,-34.364114, 149.166022, 30)

    :param target_system: This can be set to any value
        (DroneKit changes the value to the MAVLink ID of the connected vehicle before the command is sent).
    :param target_component: The component id if the message is intended for a particular component within
        the target system (for example, the camera). Set to zero (broadcast) in most cases.
    :param seq: The sequence number within the mission (the autopilot will reject messages sent out of sequence).
        This should be set to zero as the API will automatically set the correct value when uploading a mission.
    :param frame: The frame of reference used for the location parameters (x, y, z). In most cases this will be
        ``mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT``, which uses the WGS84 global coordinate system for
        latitude and longitude, but sets altitude as relative to the home position in metres (home altitude = 0).
        For more information `see the wiki here
        <http://planner.ardupilot.com/wiki/common-mavlink-mission-command-messages-mav_cmd/#frames_of_reference>`_.
    :param command: The specific mission command (e.g. ``mavutil.mavlink.MAV_CMD_NAV_WAYPOINT``). The supported
        commands (and command parameters are listed `on the wiki
        <http://planner.ardupilot.com/wiki/common-mavlink-mission-command-messages-mav_cmd/>`_.
    :param current: Set to zero (not supported).
    :param autocontinue: Set to zero (not supported).
    :param param1: Command specific parameter (depends on specific `Mission Command (MAV_CMD) <http://planner.ardupilot.com/wiki/common-mavlink-mission-command-messages-mav_cmd/>`_).
    :param param2: Command specific parameter.
    :param param3: Command specific parameter.
    :param param4: Command specific parameter.
    :param x: (param5) Command specific parameter used for latitude (if relevant to command).
    :param y: (param6) Command specific parameter used for longitude (if relevant to command).
    :param z: (param7) Command specific parameter used for altitude (if relevant). The reference frame for
        altitude depends on the ``frame``.

    """

    pass


class CommandInt(mavutil.mavlink.MAVLink_mission_item_int_message):
    """
    A waypoint object using the integer-encoded ``MISSION_ITEM_INT`` wire format.

    This is the same mission-item concept as :py:class:`Command` (the same fields, in the same
    order), but ``x``/``y`` (latitude/longitude) are transmitted as ``int32`` values holding
    degrees multiplied by 1e7, instead of :py:class:`Command`'s ``float32`` degrees. Use
    ``CommandInt`` instead of :py:class:`Command` when a mission needs consistent centimetre-scale
    precision rather than float32's roughly decimetre-scale precision.

    **Why this matters, with real numbers.** float32 carries only ~7 significant decimal digits.
    Encoding the coordinate pair used in :py:class:`Command`'s own docstring example
    (``-34.364114, 149.166022`` - 8 significant digits each) through
    ``struct.unpack('f', struct.pack('f', value))[0]`` and comparing to the original value gives:

    * latitude ``-34.364114`` -> ``-34.364112854003906``, an error of about **12.8 cm** on the ground.
    * longitude ``149.166022`` -> ``149.166015625``, an error of about **71.0 cm** on the ground
      (longitude error varies with which mantissa bits round; it is not always this large, but it
      is not bounded to sub-centimetre either - that is exactly the problem ``CommandInt`` fixes).

    The ``int32 x 1e7`` encoding used by ``MISSION_ITEM_INT`` has a fixed resolution of 1e-7
    degree per unit, which is **~1.11 cm** at the equator (and finer moving towards the poles,
    since a degree of longitude shrinks with latitude while a degree of latitude stays constant).
    For the coordinate above, round-tripping through ``int(round(value * 1e7))`` and back is exact
    to within that fixed 1.11 cm grid - no float32 mantissa rounding is involved at all.

    Aside from the ``x``/``y`` encoding, ``CommandInt`` is built exactly like :py:class:`Command`:
    same constructor, same argument order, same way of being added to a mission.

    .. code:: python

        cmd_int = CommandInt(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
            mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0,
            int(-34.364114 * 1e7), int(149.166022 * 1e7), 30)

    Most users will not want to hand-compute that ``* 1e7`` scaling. Build a normal
    :py:class:`Command` as usual and convert it with :py:meth:`CommandInt.from_command`:

    .. code:: python

        cmd = Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
            mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, -34.364114, 149.166022, 30)
        cmd_int = CommandInt.from_command(cmd)
        cmds.add(cmd_int)

    :param target_system: This can be set to any value
        (DroneKit changes the value to the MAVLink ID of the connected vehicle before the command is sent).
    :param target_component: The component id if the message is intended for a particular component
        within the target system (for example, the camera). Set to zero (broadcast) in most cases.
    :param seq: The sequence number within the mission (the autopilot will reject messages sent out of sequence).
        This should be set to zero as the API will automatically set the correct value when uploading a mission.
    :param frame: The frame of reference used for the location parameters (x, y, z).
        See :py:class:`Command` for details.
    :param command: The specific mission command (e.g. ``mavutil.mavlink.MAV_CMD_NAV_WAYPOINT``).
        See :py:class:`Command` for details.
    :param current: Set to zero (not supported).
    :param autocontinue: Set to zero (not supported).
    :param param1: Command specific parameter (depends on specific `Mission Command (MAV_CMD) <http://planner.ardupilot.com/wiki/common-mavlink-mission-command-messages-mav_cmd/>`_).
    :param param2: Command specific parameter.
    :param param3: Command specific parameter.
    :param param4: Command specific parameter.
    :param x: (param5) Latitude in degrees, multiplied by 1e7 and rounded to the nearest ``int32``
        (e.g. latitude ``-34.364114`` is passed as ``-343641140``). Prefer :py:meth:`from_command`
        over computing this by hand.
    :param y: (param6) Longitude in degrees, multiplied by 1e7 and rounded to the nearest ``int32``
        (e.g. longitude ``149.166022`` is passed as ``1491660220``). Prefer :py:meth:`from_command`
        over computing this by hand.
    :param z: (param7) Command specific parameter used for altitude (if relevant). Same units/frame
        semantics as :py:class:`Command` - unlike x/y, z is a plain float in both message types.

    """

    @classmethod
    def from_command(cls, cmd: Command) -> CommandInt:
        """
        Build a :py:class:`CommandInt` from an existing :py:class:`Command`, converting its
        float-degree ``x``/``y`` into the ``int32 x 1e7`` representation ``CommandInt`` needs.

        This is the recommended way to opt in to :py:class:`CommandInt`'s precision: build (or
        receive) an ordinary :py:class:`Command` as usual, then convert it just before adding it
        to the mission, instead of hand-computing the ``* 1e7`` scaling yourself.

        :param cmd: The :py:class:`Command` (or any object exposing the same field names -
            a plain pymavlink ``MAVLink_mission_item_message`` works too) to convert.
        :return: An equivalent :py:class:`CommandInt`, with ``x``/``y`` rescaled to ``int32``.
        """
        return cls(
            cmd.target_system,
            cmd.target_component,
            cmd.seq,
            cmd.frame,
            cmd.command,
            cmd.current,
            cmd.autocontinue,
            cmd.param1,
            cmd.param2,
            cmd.param3,
            cmd.param4,
            int(round(cmd.x * 1e7)),
            int(round(cmd.y * 1e7)),
            cmd.z,
        )


class CommandSequence:
    """
    A sequence of vehicle waypoints (a "mission").

    Operations include 'array style' indexed access to the various contained waypoints.

    The current commands/mission for a vehicle are accessed using the :py:attr:`Vehicle.commands` attribute.
    Waypoints are not downloaded from vehicle until :py:func:`download()` is called.  The download is asynchronous;
    use :py:func:`wait_ready()` to block your thread until the download is complete.
    The code to download the commands from a vehicle is shown below:

    .. code-block:: python
        :emphasize-lines: 5-10

        #Connect to a vehicle object (for example, on com14)
        vehicle = connect('com14', wait_ready=True)

        # Download the vehicle waypoints (commands). Wait until download is complete.
        cmds = vehicle.commands
        cmds.download()
        cmds.wait_ready()

    The set of commands can be changed and uploaded to the client. The changes are not guaranteed to be complete until
    :py:func:`upload() <Vehicle.commands.upload>` is called.

    .. code:: python

        cmds = vehicle.commands
        cmds.clear()
        lat = -34.364114,
        lon = 149.166022
        altitude = 30.0
        cmd = Command(0,0,0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,
            0, 0, 0, 0, 0, 0,
            lat, lon, altitude)
        cmds.add(cmd)
        cmds.upload()

    """

    def __init__(self, vehicle: VehicleLike) -> None:
        self._vehicle = vehicle

    def download(self) -> None:
        """
        Download all waypoints from the vehicle.
        The download is asynchronous. Use :py:func:`wait_ready()` to block your thread until the download is complete.
        """
        self.wait_ready()
        self._vehicle._ready_attrs.remove("commands")
        self._vehicle._wp_loaded = False
        self._vehicle._wp_download_in_progress = True
        self._vehicle._master.waypoint_request_list_send()
        # BIG FIXME - wait for full wpt download before allowing any of the accessors to work

    def wait_ready(self, **kwargs: Any) -> bool:
        """
        Block the calling thread until waypoints have been downloaded.

        This can be called after :py:func:`download()` to block the thread until the asynchronous download is complete.
        """
        return self._vehicle.wait_ready("commands", **kwargs)

    def clear(self) -> None:
        """
        Clear the command list.

        This command will be sent to the vehicle only after you call :py:func:`upload() <Vehicle.commands.upload>`.
        """

        # Add home point again.
        self.wait_ready()
        home = None
        try:
            home = self._vehicle._wploader.wp(0)
        except Exception:
            pass
        self._vehicle._wploader.clear()
        if home:
            self._vehicle._wploader.add(home, comment="Added by DroneKit")
        self._vehicle._wpts_dirty = True

    def add(self, cmd: Command | CommandInt) -> None:
        """
        Add a new command (waypoint) at the end of the command list.

        .. note::

            Commands are sent to the vehicle only after you call ::py:func:`upload() <Vehicle.commands.upload>`.

        :param cmd: The command to be added: either a :py:class:`Command` (float32 ``MISSION_ITEM``,
            the default) or a :py:class:`CommandInt` (int32 x 1e7 ``MISSION_ITEM_INT``, for
            centimetre-precision uploads). Both are accepted interchangeably - the underlying
            waypoint loader (and the upload path built on it) only ever calls generic,
            message-class-agnostic operations (``.clear()``, ``.count()``, ``.add()``, ``.wp()``,
            ``.set()``, keyed purely by ``.seq``), so nothing here requires the float variant
            specifically.
        """
        self.wait_ready()
        self._vehicle._handler.fix_targets(cmd)
        self._vehicle._wploader.add(cmd, comment="Added by DroneKit")
        self._vehicle._wpts_dirty = True

    def upload(self, timeout: float | None = None) -> None:
        """
        Call ``upload()`` after :py:func:`adding <CommandSequence.add>` or
        :py:func:`clearing <CommandSequence.clear>` mission commands.

        After the return from ``upload()`` any writes are guaranteed to have completed (or thrown an
        exception) and future reads will see their effects.

        :param int timeout: The timeout for uploading the mission. No timeout if not provided or set to None.
        """
        if self._vehicle._wpts_dirty:
            self._vehicle._master.waypoint_clear_all_send()
            start_time = time.monotonic()
            if self._vehicle._wploader.count() > 0:
                self._vehicle._wp_uploaded = [False] * self._vehicle._wploader.count()
                self._vehicle._master.waypoint_count_send(self._vehicle._wploader.count())
                while False in self._vehicle._wp_uploaded:
                    if timeout and time.monotonic() - start_time > timeout:
                        raise TimeoutError
                    time.sleep(0.1)
                self._vehicle._wp_uploaded = None
            self._vehicle._wpts_dirty = False

    @property
    def count(self) -> int:
        """
        Return number of waypoints.

        :return: The number of waypoints in the sequence.
        """
        return max(self._vehicle._wploader.count() - 1, 0)

    @property
    def next(self) -> int:
        """
        Get the currently active waypoint number.
        """
        return self._vehicle._current_waypoint

    @next.setter
    def next(self, index: int) -> None:
        """
        Set a new ``next`` waypoint for the vehicle.
        """
        self._vehicle._master.waypoint_set_current_send(index)

    def _raise_if_download_in_progress(self) -> None:
        if self._vehicle._wp_download_in_progress:
            raise APIException(
                "CommandSequence was read while a commands.download() was still in "
                "progress. Call commands.wait_ready() after download() before reading "
                "commands, len(), or indexing them."
            )

    def __len__(self) -> int:
        """
        Return number of waypoints.

        :return: The number of waypoints in the sequence.
        """
        self._raise_if_download_in_progress()
        return max(self._vehicle._wploader.count() - 1, 0)

    def __getitem__(self, index: int | slice) -> Any:
        self._raise_if_download_in_progress()
        if isinstance(index, slice):
            return [self[ii] for ii in range(*index.indices(len(self)))]
        elif isinstance(index, int):
            item = self._vehicle._wploader.wp(index + 1)
            if not item:
                raise IndexError(f"Index {index} out of range.")
            return item
        else:
            raise TypeError("Invalid argument type.")

    def __setitem__(self, index: int, value: Any) -> None:
        self._vehicle._wploader.set(value, index + 1)
        self._vehicle._wpts_dirty = True
