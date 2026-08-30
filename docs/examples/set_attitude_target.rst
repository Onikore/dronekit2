.. _example_set_attitude_target:

============================
Example: Set Attitude Target
============================

This example arms and takes off in ``GUIDED_NOGPS`` mode, then directly commands roll/pitch/yaw
and thrust via ``SET_ATTITUDE_TARGET`` - useful on vehicles/simulations where GPS-based
positioning (``simple_goto``, missions) isn't available or desired.

.. warning::

    A lot of unexpected behaviour can occur in ``GUIDED_NOGPS`` mode. Always watch the vehicle
    closely, fly somewhere safe, and land immediately if it does anything unexpected.


Running the example
====================

The example can be run as described in :doc:`running_examples` (which in turn assumes that the
vehicle and DroneKit have been set up as described in :ref:`installing_dronekit`).

In summary, after cloning the repository:

#. Navigate to the example folder as shown:

   .. code-block:: bash

       cd dronekit2/examples/set_attitude_target/

#. Start an ArduPilot SITL instance yourself first (see :ref:`sitl_setup`), then run the example
   passing its connection string:

   .. code-block:: bash

       python set_attitude_target.py --connect udp:127.0.0.1:14550

   The vehicle takes off to 2.5m, holds, pitches forward then backward, lands, and the script
   exits.


How does it work?
===================

``set_attitude_target()`` builds and sends a ``SET_ATTITUDE_TARGET`` message directly, converting
roll/pitch/yaw (in degrees) into the quaternion the message wants:

.. code-block:: python

    msg = vehicle.message_factory.set_attitude_target_encode(
        0,  # time_boot_ms
        1,  # Target system
        1,  # Target component
        0b00000000 if use_yaw_rate else 0b00000100,
        to_quaternion(roll_angle, pitch_angle, yaw_angle),  # Quaternion
        0,  # Body roll rate in radian
        0,  # Body pitch rate in radian
        math.radians(yaw_rate),  # Body yaw rate in radian/second
        thrust,  # Thrust
    )
    vehicle.send_mavlink(msg)

``set_attitude()`` re-sends this at 10Hz for the requested ``duration`` - an
``ATTITUDE_TARGET`` order has a 1-second timeout on ArduCopter, so a single send would only hold
the attitude briefly - then resets to level/hover thrust so the attitude doesn't persist past
the call.


Source code
===========

The full source code at documentation build-time is listed below
(`current version on Github <https://github.com/Onikore/dronekit2/blob/main/examples/set_attitude_target/set_attitude_target.py>`_):

.. literalinclude:: ../../examples/set_attitude_target/set_attitude_target.py
    :language: python
