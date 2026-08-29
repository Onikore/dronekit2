"""RC channel and channel-override dictionaries associated with a Vehicle."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from dronekit.protocols import VehicleLike


class ChannelsOverride(dict):
    """
    A dictionary class for managing Vehicle channel overrides.

    Channels can be read, written, or cleared by index or using a dictionary syntax.
    To clear a value, set it to ``None`` or use ``del`` on the item.

    An object of this type is returned by :py:attr:`Vehicle.channels.overrides <Channels.overrides>`.

    For more information and examples see :ref:`example_channel_overrides`.
    """

    def __init__(self, vehicle: VehicleLike) -> None:
        self._vehicle = vehicle
        self._count = 8  # Fixed by MAVLink
        self._active = True

    def __getitem__(self, key: Any) -> Any:
        return dict.__getitem__(self, str(key))

    def __setitem__(self, key: Any, value: Any) -> None:
        if not (0 < int(key) <= self._count):
            raise KeyError(f'Invalid channel index {key}')
        if not value:
            try:
                dict.__delitem__(self, str(key))
            except Exception:
                pass
        else:
            dict.__setitem__(self, str(key), value)
        self._send()

    def __delitem__(self, key: Any) -> None:
        dict.__delitem__(self, str(key))
        self._send()

    def __len__(self) -> int:
        return self._count

    def _send(self) -> None:
        if self._active:
            overrides = [0] * 8
            for k, v in self.items():
                overrides[int(k) - 1] = v
            self._vehicle._master.mav.rc_channels_override_send(0, 0, *overrides)


class Channels(dict):
    """
    A dictionary class for managing RC channel information associated with a :py:class:`Vehicle`.

    An object of this type is accessed through :py:attr:`Vehicle.channels`. This object also stores
    the current vehicle channel overrides through its :py:attr:`overrides` attribute.

    For more information and examples see :ref:`example_channel_overrides`.
    """

    def __init__(self, vehicle: VehicleLike, count: int) -> None:
        self._vehicle = vehicle
        self._count = count
        self._overrides = ChannelsOverride(vehicle)

        # populate readback
        self._readonly = False
        for k in range(0, count):
            self[k + 1] = None
        self._readonly = True

    @property
    def count(self) -> int:
        """
        The number of channels defined in the dictionary (currently 8).
        """
        return self._count

    def __getitem__(self, key: Any) -> Any:
        return dict.__getitem__(self, str(key))

    def __setitem__(self, key: Any, value: Any) -> None:
        if self._readonly:
            raise TypeError('__setitem__ is not supported on Channels object')
        return dict.__setitem__(self, str(key), value)

    def __len__(self) -> int:
        return self._count

    def _update_channel(self, channel: Any, value: Any) -> None:
        # If we have channels on different ports, we expand the Channels
        # object to support them.
        channel = int(channel)
        self._readonly = False
        self[channel] = value
        self._readonly = True
        self._count = max(self._count, channel)

    @property
    def overrides(self) -> ChannelsOverride:
        """
        Attribute to read, set and clear channel overrides (also known as "rc overrides")
        associated with a :py:class:`Vehicle` (via :py:class:`Vehicle.channels`). This is an
        object of type :py:class:`ChannelsOverride`.

        For more information and examples see :ref:`example_channel_overrides`.

        To set channel overrides:

        .. code:: python

            # Set and clear overrids using dictionary syntax (clear by setting override to none)
            vehicle.channels.overrides = {'5':None, '6':None,'3':500}

            # You can also set and clear overrides using indexing syntax
            vehicle.channels.overrides['2'] = 200
            vehicle.channels.overrides['2'] = None

            # Clear using 'del'
            del vehicle.channels.overrides['3']

            # Clear all overrides by setting an empty dictionary
            vehicle.channels.overrides = {}

        Read the channel overrides either as a dictionary or by index. Note that you'll get
        a ``KeyError`` exception if you read a channel override that has not been set.

        .. code:: python

            # Get all channel overrides
            print " Channel overrides: %s" % vehicle.channels.overrides
            # Print just one channel override
            print " Ch2 override: %s" % vehicle.channels.overrides['2']
        """
        return self._overrides

    @overrides.setter
    def overrides(self, newch: Mapping[Any, Any]) -> None:
        self._overrides._active = False
        self._overrides.clear()
        for k, v in newch.items():
            if v:
                self._overrides[str(k)] = v
            else:
                try:
                    del self._overrides[str(k)]
                except Exception:
                    pass
        self._overrides._active = True
        self._overrides._send()
