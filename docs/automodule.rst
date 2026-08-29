.. _api_reference:

=============================
DroneKit-Python API Reference
=============================

.. automodule:: dronekit

The sections below document the public API. Since the E5 package split, ``dronekit`` is a
real package (not a single ``dronekit/__init__.py`` file) - ``dronekit/__init__.py`` is a thin
re-export facade over the submodules listed here, so every name below is still importable
directly from ``dronekit`` (e.g. ``from dronekit import Vehicle, connect``) exactly as before.


Connecting
==========

.. automodule:: dronekit.connect
   :members:


Vehicle
=======

.. automodule:: dronekit.vehicle
   :members:
   :inherited-members:


Vehicle state
=============

.. automodule:: dronekit.types
   :members:


Channels
========

.. automodule:: dronekit.channels
   :members:


Locations
=========

.. automodule:: dronekit.locations
   :members:


Parameters
==========

.. automodule:: dronekit.parameters
   :members:


Missions
========

.. automodule:: dronekit.mission
   :members:


Gimbal
======

.. automodule:: dronekit.gimbal
   :members:


Observers
=========

.. automodule:: dronekit.observers
   :members:


Errors
======

.. automodule:: dronekit.errors
   :members:


Utilities
=========

.. automodule:: dronekit.util
   :members:


Internals
=========

.. note::

    The modules below are internal implementation details (the MAVLink connection wrapper
    and the ``Protocol`` used to break an import cycle between ``vehicle.py`` and its
    sub-objects). They are not part of the supported public API and may change without
    notice - documented here only for completeness against the real package layout.

.. automodule:: dronekit.mavlink
   :members:

.. automodule:: dronekit.protocols
   :members:


.. toctree::
   :hidden:

   genindex


.. todolist::
