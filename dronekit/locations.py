"""Global/global-relative/local location tracking for a Vehicle."""

from __future__ import annotations

import copy
from typing import Any

from dronekit.observers import HasObservers
from dronekit.protocols import VehicleLike
from dronekit.types import LocationGlobal, LocationGlobalRelative, LocationLocal


class Locations(HasObservers):
    """
    An object for holding location information in global, global relative and local frames.

    :py:class:`Vehicle` owns an object of this type. See :py:attr:`Vehicle.location` for information on
    reading and observing location in the different frames.

    The different frames are accessed through the members, which are created with this object.
    They can be read, and are observable.
    """

    def __init__(self, vehicle: VehicleLike) -> None:
        super().__init__()

        # D10: global_frame/global_relative_frame are cached here as whole,
        # immutable Location* objects and replaced with a single attribute
        # assignment on update (see listener below), instead of being
        # rebuilt on every property read from separate _lat/_lon/_alt scalar
        # fields. `self._x = LocationGlobal(...)` is one atomic STORE_ATTR
        # bytecode that the GIL cannot interleave with another thread's
        # execution, so a reader on another thread (e.g. polling
        # vehicle.location.global_frame) always sees either the complete old
        # object or the complete new one - never a torn combination of new
        # lat/lon paired with a stale alt (or vice-versa), which was
        # possible when lat/lon/alt were three separate instance attributes
        # updated by three separate statements in this same listener.
        self._global_frame = LocationGlobal(None, None, None)
        self._global_relative_frame = LocationGlobalRelative(None, None, None)

        @vehicle.on_message("GLOBAL_POSITION_INT")
        def listener(vehicle: VehicleLike, name: str, m: Any) -> None:
            lat = m.lat / 1.0e7
            lon = m.lon / 1.0e7

            self._global_relative_frame = LocationGlobalRelative(lat, lon, m.relative_alt / 1000.0)
            self.notify_attribute_listeners("global_relative_frame", self.global_relative_frame)
            vehicle.notify_attribute_listeners("location.global_relative_frame", vehicle.location.global_relative_frame)

            if self._global_frame.alt is not None or m.alt != 0:
                # Require first alt value to be non-0
                # TODO is this the proper check to do?
                self._global_frame = LocationGlobal(lat, lon, m.alt / 1000.0)
                self.notify_attribute_listeners("global_frame", self.global_frame)
                vehicle.notify_attribute_listeners("location.global_frame", vehicle.location.global_frame)

            vehicle.notify_attribute_listeners("location", vehicle.location)

        self._north: float | None = None
        self._east: float | None = None
        self._down: float | None = None

        @vehicle.on_message("LOCAL_POSITION_NED")
        def listener(vehicle: VehicleLike, name: str, m: Any) -> None:  # noqa: F811 - consumed immediately by the decorator above, not a real redefinition
            self._north = m.x
            self._east = m.y
            self._down = m.z
            self.notify_attribute_listeners("local_frame", self.local_frame)
            vehicle.notify_attribute_listeners("location.local_frame", vehicle.location.local_frame)
            vehicle.notify_attribute_listeners("location", vehicle.location)

    @property
    def local_frame(self) -> LocationLocal:
        """
        Location in local NED frame (a :py:class:`LocationGlobalRelative`).

        This is accessed through the :py:attr:`Vehicle.location` attribute:

        .. code-block:: python

            print "Local Location: %s" % vehicle.location.local_frame

        This location will not start to update until the vehicle is armed.
        """
        return LocationLocal(self._north, self._east, self._down)

    @property
    def global_frame(self) -> LocationGlobal:
        """
        Location in global frame (a :py:class:`LocationGlobal`).

        The latitude and longitude are relative to the
        `WGS84 coordinate system <http://en.wikipedia.org/wiki/World_Geodetic_System>`_.
        The altitude is relative to mean sea-level (MSL).

        This is accessed through the :py:attr:`Vehicle.location` attribute:

        .. code-block:: python

            print "Global Location: %s" % vehicle.location.global_frame
            print "Sea level altitude is: %s" % vehicle.location.global_frame.alt

        Its ``lat`` and ``lon`` attributes are populated shortly after GPS becomes available.
        The ``alt`` can take several seconds longer to populate (from the barometer).
        Listeners are not notified of changes to this attribute until it has fully populated.

        To watch for changes you can use :py:func:`Vehicle.on_attribute` decorator or
        :py:func:`add_attribute_listener` (decorator approach shown below):

        .. code-block:: python

            @vehicle.on_attribute('location.global_frame')
            def listener(self, attr_name, value):
                print " Global: %s" % value

            #Alternatively, use decorator: ``@vehicle.location.on_attribute('global_frame')``.
        """
        # Single atomic read of the cached object (see D10 note in
        # __init__ above), then a shallow copy so callers mutating the
        # returned object can't corrupt the cached value - the same
        # pattern already used by Vehicle.home_location.
        return copy.copy(self._global_frame)

    @property
    def global_relative_frame(self) -> LocationGlobalRelative:
        """
        Location in global frame, with altitude relative to the home location
        (a :py:class:`LocationGlobalRelative`).

        The latitude and longitude are relative to the
        `WGS84 coordinate system <http://en.wikipedia.org/wiki/World_Geodetic_System>`_.
        The altitude is relative to :py:attr:`home location <Vehicle.home_location>`.

        This is accessed through the :py:attr:`Vehicle.location` attribute:

        .. code-block:: python

            print "Global Location (relative altitude): %s" % vehicle.location.global_relative_frame
            print "Altitude relative to home_location: %s" % vehicle.location.global_relative_frame.alt
        """
        return copy.copy(self._global_relative_frame)
