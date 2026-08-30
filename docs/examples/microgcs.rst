.. _example_microgcs:

===================
Example: microGCS
===================

A tiny Tkinter-based ground station: a window with three labels (location, attitude, mode) that
update live via attribute listeners, and buttons to switch the vehicle between a few flight
modes. Self-described in its own source as "the world's crummiest GCS" - useful as a minimal,
readable starting point for a custom GUI, not as a serious ground station.

.. note::

    Needs a Tkinter-capable Python (the standard CPython installers on Windows/macOS include it;
    on Linux you may need to install a ``python3-tk`` -style package separately) and a display to
    show the window on.


Running the example
====================

The example can be run as described in :doc:`running_examples` (which in turn assumes that the
vehicle and DroneKit have been set up as described in :ref:`installing_dronekit`).

In summary, after cloning the repository:

#. Navigate to the example folder as shown:

   .. code-block:: bash

       cd dronekit2/examples/gcs/

#. Start an ArduPilot SITL instance yourself first (see :ref:`sitl_setup`), then run the example
   passing its connection string:

   .. code-block:: bash

       python microgcs.py --connect udp:127.0.0.1:14550

   A small window opens showing the vehicle's location and attitude, updating as new telemetry
   arrives, with buttons to change flight mode.


How does it work?
===================

Each telemetry label is wired up with :py:func:`Vehicle.add_attribute_listener()
<dronekit.Vehicle.add_attribute_listener>`, called once at startup to seed an initial value and
again every time the attribute changes:

.. code-block:: python

    def addObserverAndInit(name, cb):
        """We go ahead and call our observer once at startup to get an initial value"""
        vehicle.add_attribute_listener(name, cb)

    addObserverAndInit("attitude", lambda vehicle, name, attitude: updateGUI(attitudeLabel, vehicle.attitude))
    addObserverAndInit("location", lambda vehicle, name, location: updateGUI(locationLabel, str(location.global_frame)))

Mode-change buttons just set :py:attr:`Vehicle.mode <dronekit.Vehicle.mode>` directly.


Source code
===========

The full source code at documentation build-time is listed below
(`current version on Github <https://github.com/Onikore/dronekit2/blob/main/examples/gcs/microgcs.py>`_):

.. literalinclude:: ../../examples/gcs/microgcs.py
    :language: python
