.. _example_reboot:

================
Example: Reboot
================

A minimal example that connects to a vehicle and calls
:py:func:`Vehicle.reboot() <dronekit.Vehicle.reboot>`, then exits.


Running the example
====================

The example can be run as described in :doc:`running_examples` (which in turn assumes that the
vehicle and DroneKit have been set up as described in :ref:`installing_dronekit`).

In summary, after cloning the repository:

#. Navigate to the example folder as shown:

   .. code-block:: bash

       cd dronekit2/examples/reboot/

#. Start an ArduPilot SITL instance yourself first (see :ref:`sitl_setup`), then run the example
   passing its connection string:

   .. code-block:: bash

       python reboot.py --connect udp:127.0.0.1:14550


How does it work?
===================

The whole example is two lines once connected:

.. code-block:: python

    vehicle.reboot()
    time.sleep(1)

The ``sleep`` just gives the reboot command time to actually reach the autopilot before the
script (and its connection) exits.


Source code
===========

The full source code at documentation build-time is listed below
(`current version on Github <https://github.com/Onikore/dronekit2/blob/main/examples/reboot/reboot.py>`_):

.. literalinclude:: ../../examples/reboot/reboot.py
    :language: python
