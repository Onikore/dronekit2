"""Structural type for the surface of Vehicle used by its sub-objects.

Channels/ChannelsOverride, Locations, Parameters, CommandSequence, and
Gimbal each hold a reference to the owning Vehicle (as ``self._vehicle``,
or as the ``vehicle`` constructor/closure argument) and reach back into
it for a small, fixed set of attributes and methods. If those modules
imported the concrete ``dronekit.vehicle.Vehicle`` class to type-hint
that reference, ``dronekit/vehicle.py`` (which constructs concrete
Channels/Locations/Parameters/CommandSequence/Gimbal instances) would
import them, and they would import vehicle.py back - a circular import.

``VehicleLike`` breaks that cycle: it is a ``typing.Protocol`` declaring
only the members those sub-objects actually access on a vehicle
(derived by grepping ``_vehicle\\.`` and the closure-captured ``vehicle.``
uses across the original monolithic dronekit/__init__.py, not guessed).
The sub-object modules type-hint against this protocol instead of the
concrete class, so they have no import-time dependency on vehicle.py at
all - only vehicle.py imports them, one direction, no cycle.
"""

from typing import Any, Callable, Optional, Protocol


class VehicleLike(Protocol):
    """The subset of Vehicle's interface reached into by its sub-objects."""

    # -- attributes --------------------------------------------------
    _master: Any
    _handler: Any
    _params_map: dict
    _ready_attrs: set
    _wploader: Any
    _wp_loaded: bool
    _wp_download_in_progress: bool
    _wp_uploaded: Optional[list]
    _wpts_dirty: bool
    _current_waypoint: int

    # Self-referential properties: `vehicle.location` returns the owning
    # Locations instance, `vehicle.gimbal` returns the owning Gimbal
    # instance. Typed loosely to avoid importing locations.py/gimbal.py
    # here (which would reintroduce the very cycle this module exists to
    # avoid).
    location: Any
    gimbal: Any

    # The pymavlink message-factory object (`vehicle._master.mav`).
    message_factory: Any

    # -- methods -------------------------------------------------------
    def wait_ready(self, *types: Any, **kwargs: Any) -> bool: ...

    def on_message(self, name: Any) -> Callable[[Callable[..., Any]], None]: ...

    def notify_attribute_listeners(self, attr_name: str, value: Any, cache: bool = False) -> None: ...

    def send_mavlink(self, message: Any) -> None: ...
