.. _migrating_v3:

==========================================
Migrating to dronekit2 (from DroneKit 2.x)
==========================================

This fork (PyPI package ``dronekit2``, source at `github.com/Onikore/dronekit2
<https://github.com/Onikore/dronekit2>`_) picks up maintenance of DroneKit-Python after the
upstream ``dronekit`` / ``dronekit-python`` project went dormant. This page documents the
breaking (and non-breaking-but-notable) changes between the last upstream 2.9.x releases and
this fork, for people upgrading existing scripts.

.. tip::

    If you're migrating from *DroneKit-Python 1.x* rather than 2.x, see
    :ref:`migrating_dkpy2_0` instead - that migration (MAVProxy-hosted scripts to standalone
    scripts) predates this fork and still applies unchanged.


PyPI package renamed - import name unchanged
==============================================

The package on PyPI is now ``dronekit2``:

.. code-block:: bash

    pip install dronekit2

The **import name has not changed** - your code still does ``import dronekit`` /
``from dronekit import connect, VehicleMode`` exactly as before. Nothing in application code
needs to change because of the rename.


Python 3.9+ required
=====================

This fork requires **Python 3.9 or later**. Support for Python 2.7 and for Python 3 versions
older than 3.9 has been dropped. See :ref:`installing_dronekit`.


Internal package split - no user-facing change
=================================================

Historically, the entire ``dronekit`` public API (``Vehicle``, ``connect()``, ``Command``,
``Channels``, ``Parameters``, ``Locations``, ``Gimbal``, the attribute/location/battery types,
and so on) lived in a single, very large ``dronekit/__init__.py`` file.

That file has been split into a real package, organised by concern:

* :file:`dronekit/errors.py` - ``APIException``, ``TimeoutError``.
* :file:`dronekit/types.py` - value types (``Attitude``, ``LocationGlobal``, ``GPSInfo``, ``Battery``, ``VehicleMode``, etc.).
* :file:`dronekit/observers.py` - the ``HasObservers`` attribute-listener mixin.
* :file:`dronekit/channels.py`, :file:`locations.py`, :file:`parameters.py`, :file:`mission.py`, :file:`gimbal.py` - the ``Vehicle`` sub-objects.
* :file:`dronekit/vehicle.py` - the ``Vehicle`` class itself.
* :file:`dronekit/connect.py` - the ``connect()`` entry point.
* :file:`dronekit/mavlink.py`, :file:`dronekit/protocols.py`, :file:`dronekit/util.py` - internal plumbing (MAVLink connection handling, a typing ``Protocol`` used to avoid an import cycle, small logging helpers).

``dronekit/__init__.py`` is now a thin re-export facade over these submodules - every name
that used to be importable from ``dronekit`` still is:

.. code-block:: python

    # Still works exactly as before - nothing to change here.
    from dronekit import connect, Vehicle, VehicleMode, Command, LocationGlobalRelative

If your code only ever imported from the top-level ``dronekit`` package (the documented,
supported way), **this change is invisible to you**. It only matters if you were reaching into
private submodule paths that didn't exist as a public interface before either (e.g. importing
directly from wherever a class happened to be defined inside the old monolithic file) - there
was never a supported way to do that, and there still isn't.

See :ref:`api_reference` for the full reference, now organised by these same submodules.


``status_printer`` / ``errprinter``
======================================

:py:func:`connect() <dronekit.connect>` still accepts a ``status_printer`` keyword argument,
and it still works exactly as before - but it remains **deprecated**, as it already was
upstream. It exists only to redirect ``STATUSTEXT`` messages from the vehicle (and other
library diagnostics) to a callback of signature ``def status_printer(txt)``.

.. code-block:: python

    # Still supported, still deprecated:
    vehicle = connect(connection_string, status_printer=my_print_function)

The modern replacement is to configure Python's standard ``logging`` module directly - attach
handlers/formatters to the ``dronekit`` and ``autopilot`` loggers instead of passing a
callback:

.. code-block:: python

    import logging
    logging.getLogger('autopilot').addHandler(logging.StreamHandler())

There is no separate ``errprinter`` keyword argument to ``connect()`` in this fork - if you're
coming from very old (pre-2.0) DroneKit-Python code that used one, see
:ref:`migrating_dkpy2_0` for that migration; it does not exist as connect() surface here to
remove. The name survives only as internal implementation detail: ``dronekit.util`` has a
small ``ErrprinterHandler`` (a ``logging.Handler``) that adapts the deprecated
``status_printer`` callback onto the ``logging`` machinery, plus two tiny stderr-printing
helper functions. None of these three are exported from ``dronekit`` and were never part of
the supported public API - nothing to migrate away from there either.


New: ``CommandInt`` for centimetre-precision missions
=========================================================

:py:class:`Command <dronekit.Command>` mission items encode latitude/longitude as ``float32``
degrees. ``float32`` only carries about 7 significant decimal digits, which works out to
roughly **decimetre-scale** rounding error on real-world coordinates - usually fine, but not
always tight enough for precision-landing or survey-style missions.

This fork adds :py:class:`CommandInt <dronekit.CommandInt>`, which encodes the same mission
item over the MAVLink ``MISSION_ITEM_INT`` wire format: latitude/longitude as ``int32`` degrees
x 1e7, giving a fixed **~1.11 cm** resolution at the equator with no float32 mantissa rounding
involved. It's a drop-in alternative to ``Command`` - same constructor shape, same way of being
added to a mission via :py:attr:`Vehicle.commands <dronekit.Vehicle.commands>`. The easiest way
to adopt it is to build a normal ``Command`` and convert it:

.. code-block:: python

    from dronekit import Command, CommandInt

    cmd = Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
        mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, -34.364114, 149.166022, 30)
    cmd_int = CommandInt.from_command(cmd)
    vehicle.commands.add(cmd_int)

Existing code using plain ``Command`` needs no changes - ``CommandInt`` is purely additive.


SITL tooling: ``dronekit-sitl`` is gone
==========================================

The ``dronekit-sitl`` pip package (which downloaded and ran pre-built ArduPilot SITL binaries)
is dead - its binary host no longer serves files. Scripts and tests that used to do
``import dronekit_sitl; sitl = dronekit_sitl.start_default()`` need to be updated to connect to
a SITL instance you start yourself. See :ref:`sitl_setup` for how to build and run ArduPilot
SITL directly (the same approach this project's own CI now uses), and
:file:`dronekit/test/conftest.py` for how the test suite's ``DRONEKIT_TEST_CONNECTION``
environment variable works if you're adapting test code specifically.
