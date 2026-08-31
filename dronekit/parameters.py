"""Editable named-parameter mapping for a Vehicle."""

from __future__ import annotations

import logging
import struct
import time
from collections.abc import Iterator, MutableMapping
from typing import Any, Callable

from dronekit.errors import APIException
from dronekit.observers import HasObservers
from dronekit.protocols import VehicleLike


class Parameters(MutableMapping, HasObservers):
    """
    This object is used to get and set the values of named parameters for a vehicle. See the following
    links for information about the supported parameters for each platform:
    `Copter Parameters <http://copter.ardupilot.com/wiki/configuration/arducopter-parameters/>`_,
    `Plane Parameters <http://plane.ardupilot.com/wiki/arduplane-parameters/>`_, `Rover Parameters <http://rover.ardupilot.com/wiki/apmrover2-parameters/>`_.

    The code fragment below shows how to get and set the value of a parameter.

    .. code:: python

        # Print the value of the MOT_SPIN_MIN parameter.
        print(f"Param: {vehicle.parameters['MOT_SPIN_MIN']}")

        # Change the parameter value to something different.
        vehicle.parameters['MOT_SPIN_MIN'] = 0.1

    It is also possible to observe parameters and to iterate the :py:attr:`Vehicle.parameters`.

    For more information see :ref:`the guide <vehicle_state_parameters>`.
    """

    def __init__(self, vehicle: VehicleLike) -> None:
        super().__init__()
        self._logger = logging.getLogger(__name__)
        self._vehicle = vehicle

    def __getitem__(self, name: str) -> float:
        name = name.upper()
        self.wait_ready()
        return self._vehicle._params_map[name]

    def __setitem__(self, name: str, value: float) -> None:
        name = name.upper()
        self.wait_ready()
        self.set(name, value)

    def __delitem__(self, name: str) -> None:
        raise APIException("Cannot delete value from parameters list.")

    def __len__(self) -> int:
        return len(self._vehicle._params_map)

    def __iter__(self) -> Iterator[str]:
        return self._vehicle._params_map.__iter__()

    def get(self, name: str, wait_ready: bool = True) -> float | None:  # type: ignore[override]
        name = name.upper()
        if wait_ready:
            self.wait_ready()
        return self._vehicle._params_map.get(name, None)

    def set(self, name: str, value: float, retries: int = 3, wait_ready: bool = False) -> bool:
        if wait_ready:
            self.wait_ready()

        # TODO dumbly reimplement this using timeout loops
        # because we should actually be awaiting an ACK of PARAM_VALUE
        # changed, but we don't have a proper ack structure, we'll
        # instead just wait until the value itself was changed

        name = name.upper()
        # convert to single precision floating point number (the type used by low level mavlink messages)
        value = float(struct.unpack("f", struct.pack("f", value))[0])
        remaining = retries
        while True:
            self._vehicle._master.param_set_send(name, value)
            tstart = time.monotonic()
            if remaining == 0:
                break
            remaining -= 1
            while time.monotonic() - tstart < 1:
                if name in self._vehicle._params_map and self._vehicle._params_map[name] == value:
                    return True
                time.sleep(0.1)

        if retries > 0:
            self._logger.error(f"timeout setting parameter {name} to {value:f}")
        return False

    def wait_ready(self, **kwargs: Any) -> None:
        """
        Block the calling thread until parameters have been downloaded
        """
        self._vehicle.wait_ready("parameters", **kwargs)

    def add_attribute_listener(self, attr_name: str, *args: Any, **kwargs: Any) -> None:
        """
        Add a listener callback on a particular parameter.

        The callback can be removed using :py:func:`remove_attribute_listener`.

        .. note::

            The :py:func:`on_attribute` decorator performs the same operation as this method, but with
            a more elegant syntax. Use ``add_attribute_listener`` only if you will need to remove
            the observer.

        The callback function is invoked only when the parameter changes.

        The callback arguments are:

        * ``self`` - the associated :py:class:`Parameters`.
        * ``attr_name`` - the parameter name. This can be used to infer which parameter has triggered
          if the same callback is used for watching multiple parameters.
        * ``msg`` - the new parameter value (so you don't need to re-query the vehicle object).

        The example below shows how to get callbacks for the ``MOT_SPIN_MIN`` parameter:

        .. code:: python

            #Callback function for the MOT_SPIN_MIN parameter
            def mot_spin_min_callback(self, attr_name, value):
                print(f" PARAMETER CALLBACK: {attr_name} changed to: {value}")

            #Add observer for the vehicle's MOT_SPIN_MIN parameter
            vehicle.parameters.add_attribute_listener('MOT_SPIN_MIN', mot_spin_min_callback)

        See :ref:`vehicle_state_observing_parameters` for more information.

        :param String attr_name: The name of the parameter to watch (or '*' to watch all parameters).
        :param args: The callback to invoke when a change in the parameter is detected.

        """
        attr_name = attr_name.upper()
        return super().add_attribute_listener(attr_name, *args, **kwargs)

    def remove_attribute_listener(self, attr_name: str, *args: Any, **kwargs: Any) -> None:
        """
        Remove a paremeter listener that was previously added using :py:func:`add_attribute_listener`.

        For example to remove the ``mot_spin_min_callback()`` callback function:

        .. code:: python

            vehicle.parameters.remove_attribute_listener('mot_spin_min', mot_spin_min_callback)

        See :ref:`vehicle_state_observing_parameters` for more information.

        :param String attr_name: The parameter name that is to have an observer removed (or '*' to remove an
            'all attribute' observer).
        :param args: The callback function to remove.

        """
        attr_name = attr_name.upper()
        return super().remove_attribute_listener(attr_name, *args, **kwargs)

    def notify_attribute_listeners(self, attr_name: str, *args: Any, **kwargs: Any) -> None:
        attr_name = attr_name.upper()
        return super().notify_attribute_listeners(attr_name, *args, **kwargs)

    def on_attribute(self, name: str | list[str]) -> Callable[[Callable[..., Any]], None]:
        """
        Decorator for parameter listeners.

        .. note::

            There is no way to remove a listener added with this decorator. Use
            :py:func:`add_attribute_listener` if you need to be able to remove
            the :py:func:`listener <remove_attribute_listener>`.

        The callback function is invoked only when the parameter changes.

        The callback arguments are:

        * ``self`` - the associated :py:class:`Parameters`.
        * ``attr_name`` - the parameter name. This can be used to infer which parameter has triggered
          if the same callback is used for watching multiple parameters.
        * ``msg`` - the new parameter value (so you don't need to re-query the vehicle object).

        The code fragment below shows how to get callbacks for the ``MOT_SPIN_MIN`` parameter:

        .. code:: python

            @vehicle.parameters.on_attribute('MOT_SPIN_MIN')
            def decorated_mot_spin_min_callback(self, attr_name, value):
                print(f" PARAMETER CALLBACK: {attr_name} changed to: {value}")

        See :ref:`vehicle_state_observing_parameters` for more information.

        :param name: The name of the attribute to watch (or '*' to watch all attributes), or a list of names.

        """
        names = [name] if isinstance(name, str) else name
        return super().on_attribute([n.upper() for n in names])
