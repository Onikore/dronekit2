"""Gimbal (camera mount) status and control for a Vehicle."""

from __future__ import annotations

from typing import Any

from pymavlink import mavutil

from dronekit.protocols import VehicleLike
from dronekit.types import LocationGlobal, LocationGlobalRelative


class Gimbal:
    """
    Gimbal status and control.

    An object of this type is returned by :py:attr:`Vehicle.gimbal`. The
    gimbal orientation can be obtained from its :py:attr:`roll`, :py:attr:`pitch` and
    :py:attr:`yaw` attributes.

    The gimbal orientation can be set explicitly using :py:func:`rotate`
    or you can set the gimbal (and vehicle) to track a specific "region of interest" using
    :py:func:`target_location`.

    .. note::

        * The orientation attributes are created with values of ``None``. If a gimbal is present,
          the attributes are populated shortly after initialisation by messages from the autopilot.
        * The attribute values reflect the last gimbal setting-values rather than actual measured values.
          This means that the values won't change if you manually move the gimbal, and that the value
          will change when you set it, even if the specified orientation is not supported.
        * A gimbal may not support all axes of rotation. For example, the Solo gimbal will set pitch
          values from 0 to -90 (straight ahead to straight down), it will rotate the vehicle to follow specified
          yaw values, and will ignore roll commands (not supported).
    """

    def __init__(self, vehicle: VehicleLike) -> None:
        super().__init__()

        self._pitch: float | None = None
        self._roll: float | None = None
        self._yaw: float | None = None
        self._vehicle = vehicle

        @vehicle.on_message('MOUNT_STATUS')
        def listener(vehicle: VehicleLike, name: str, m: Any) -> None:
            self._pitch = m.pointing_a / 100.0
            self._roll = m.pointing_b / 100.0
            self._yaw = m.pointing_c / 100.0
            vehicle.notify_attribute_listeners('gimbal', vehicle.gimbal)

        @vehicle.on_message('MOUNT_ORIENTATION')
        def listener(vehicle: VehicleLike, name: str, m: Any) -> None:  # noqa: F811 - consumed immediately by the decorator above, not a real redefinition
            self._pitch = m.pitch
            self._roll = m.roll
            self._yaw = m.yaw
            vehicle.notify_attribute_listeners('gimbal', vehicle.gimbal)

    @property
    def pitch(self) -> float | None:
        """
        Gimbal pitch in degrees relative to the vehicle (see diagram for :ref:`attitude <figure_attitude>`).
        A value of 0 represents a camera pointed straight ahead relative to the front of the vehicle,
        while -90 points the camera straight down.

        .. note::

            This is the last pitch value sent to the gimbal (not the actual/measured pitch).
        """
        return self._pitch

    @property
    def roll(self) -> float | None:
        """
        Gimbal roll in degrees relative to the vehicle (see diagram for :ref:`attitude <figure_attitude>`).

        .. note::

            This is the last roll value sent to the gimbal (not the actual/measured roll).
        """
        return self._roll

    @property
    def yaw(self) -> float | None:
        """
        Gimbal yaw in degrees relative to *global frame* (0 is North, 90 is West, 180 is South etc).

        .. note::

            This is the last yaw value sent to the gimbal (not the actual/measured yaw).
        """
        return self._yaw

    def rotate(self, pitch: float, roll: float, yaw: float) -> None:
        """
        Rotate the gimbal to a specific vector.

        .. code-block:: python

            #Point the gimbal straight down
            vehicle.gimbal.rotate(-90, 0, 0)

        :param pitch: Gimbal pitch in degrees relative to the vehicle (see diagram for :ref:`attitude <figure_attitude>`).
            A value of 0 represents a camera pointed straight ahead relative to the front of the vehicle,
            while -90 points the camera straight down.
        :param roll: Gimbal roll in degrees relative to the vehicle (see diagram for :ref:`attitude <figure_attitude>`).
        :param yaw: Gimbal yaw in degrees relative to *global frame* (0 is North, 90 is West, 180 is South etc.)
        """
        msg = self._vehicle.message_factory.mount_configure_encode(
            0, 1,    # target system, target component
            mavutil.mavlink.MAV_MOUNT_MODE_MAVLINK_TARGETING,  #mount_mode
            1,  # stabilize roll
            1,  # stabilize pitch
            1,  # stabilize yaw
        )
        self._vehicle.send_mavlink(msg)
        msg = self._vehicle.message_factory.mount_control_encode(
            0, 1,    # target system, target component
            pitch * 100,  # pitch is in centidegrees
            roll * 100,  # roll
            yaw * 100,  # yaw is in centidegrees
            0  # save position
        )
        self._vehicle.send_mavlink(msg)

    def target_location(self, roi: LocationGlobal | LocationGlobalRelative) -> None:
        """
        Point the gimbal at a specific region of interest (ROI).

        .. code-block:: python

            #Set the camera to track the current home location.
            vehicle.gimbal.target_location(vehicle.home_location)

        The target position must be defined in a :py:class:`LocationGlobalRelative` or :py:class:`LocationGlobal`.

        This function can be called in AUTO or GUIDED mode.

        In order to clear an ROI you can send a location with all zeros (e.g. ``LocationGlobalRelative(0,0,0)``).

        :param roi: Target location in global relative frame.
        """
        # set gimbal to targeting mode
        msg = self._vehicle.message_factory.mount_configure_encode(
            0, 1,    # target system, target component
            mavutil.mavlink.MAV_MOUNT_MODE_GPS_POINT,  # mount_mode
            1,  # stabilize roll
            1,  # stabilize pitch
            1,  # stabilize yaw
        )
        self._vehicle.send_mavlink(msg)

        # Get altitude relative to home irrespective of Location object passed in.
        if isinstance(roi, LocationGlobalRelative):
            alt = roi.alt
        elif isinstance(roi, LocationGlobal):
            # NOTE (typing pass, dronekit E6): this used to read
            # `self.home_location` / `self.commands`, but Gimbal has no
            # such attributes - only the owning Vehicle does (reached via
            # VehicleLike). That path is untested and unreachable from any
            # test in dronekit/test, so it silently raised AttributeError
            # any time a caller passed a LocationGlobal here. Annotating
            # this method's signature makes mypy check the body and
            # surfaces this pre-existing bug directly, so per the task's
            # ground rule ("a type annotation is factually impossible to
            # write without a one-line correctness fix") it is corrected
            # here as the minimal fix rather than left as a new mypy error.
            if not self._vehicle.home_location:
                self._vehicle.commands.download()
                self._vehicle.commands.wait_ready()
            # Same residual gap as Vehicle.simple_goto: download()+
            # wait_ready() only block on the "commands" ready-flag, not
            # specifically on home_location becoming non-None, and
            # roi.alt can independently be None too. Pre-existing
            # (mirrors simple_goto's already-untested behavior), not
            # fixed here per the typing-only scope of this change.
            alt = roi.alt - self._vehicle.home_location.alt  # type: ignore[operator, union-attr]
        else:
            raise ValueError('Expecting location to be LocationGlobal or LocationGlobalRelative.')

        # set the ROI
        msg = self._vehicle.message_factory.command_long_encode(
            0, 1,    # target system, target component
            mavutil.mavlink.MAV_CMD_DO_SET_ROI,  # command
            0,  # confirmation
            0, 0, 0, 0,  # params 1-4
            roi.lat,
            roi.lon,
            alt
        )
        self._vehicle.send_mavlink(msg)

    def release(self) -> None:
        """
        Release control of the gimbal to the user (RC Control).

        This should be called once you've finished controlling the mount with either :py:func:`rotate`
        or :py:func:`target_location`. Control will automatically be released if you change vehicle mode.
        """
        msg = self._vehicle.message_factory.mount_configure_encode(
            0, 1,    # target system, target component
            mavutil.mavlink.MAV_MOUNT_MODE_RC_TARGETING,  # mount_mode
            1,  # stabilize roll
            1,  # stabilize pitch
            1,  # stabilize yaw
        )
        self._vehicle.send_mavlink(msg)

    def __str__(self) -> str:
        return f"Gimbal: pitch={self.pitch}, roll={self.roll}, yaw={self.yaw}"
