.. _example_play_tune:

===================
Example: Play Tune
===================

A minimal example that connects to a vehicle and plays a tune on its buzzer via
:py:func:`Vehicle.play_tune() <dronekit.Vehicle.play_tune>`.


Running the example
====================

The example can be run as described in :doc:`running_examples` (which in turn assumes that the
vehicle and DroneKit have been set up as described in :ref:`installing_dronekit`).

In summary, after cloning the repository:

#. Navigate to the example folder as shown:

   .. code-block:: bash

       cd dronekit2/examples/play_tune/

#. Start an ArduPilot SITL instance yourself first (see :ref:`sitl_setup`), then run the example
   passing its connection string:

   .. code-block:: bash

       python play_tune.py --connect udp:127.0.0.1:14550

#. Pass a custom tune with ``--tune`` (in the MML-like format ArduPilot's ``AP_Notify`` tune
   player expects). It defaults to ``AAAA`` if omitted:

   .. code-block:: bash

       python play_tune.py --connect udp:127.0.0.1:14550 --tune "L8 CDEFGAB"


How does it work?
===================

The whole example is one call once connected:

.. code-block:: python

    vehicle.play_tune(args.tune)


Source code
===========

The full source code at documentation build-time is listed below
(`current version on Github <https://github.com/Onikore/dronekit2/blob/main/examples/play_tune/play_tune.py>`_):

.. literalinclude:: ../../examples/play_tune/play_tune.py
    :language: python
