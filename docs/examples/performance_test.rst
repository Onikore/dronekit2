.. _example_performance_test:

=========================
Example: Performance Test
=========================

This example measures the round-trip latency between DroneKit sending a MAVLink command and
receiving the autopilot's ``COMMAND_ACK`` for it. It reports the running maximum, minimum, and
most recent interval for 30 seconds - useful for spotting a slow or overloaded link before it
becomes a problem in a real script.

It uses :py:func:`Vehicle.on_message() <dronekit.Vehicle.on_message>` to listen for
``COMMAND_ACK`` and :py:func:`Vehicle.send_mavlink() <dronekit.Vehicle.send_mavlink>` /
:py:attr:`Vehicle.message_factory <dronekit.Vehicle.message_factory>` to send a
``MAV_CMD_DO_SET_ROI`` command (chosen because it reliably returns an ack, not because the
command itself matters here).


Running the example
===================

The example can be run as described in :doc:`running_examples` (which in turn assumes that the
vehicle and DroneKit have been set up as described in :ref:`installing_dronekit`).

In summary, after cloning the repository:

#. Navigate to the example folder as shown:

   .. code-block:: bash

       cd dronekit2/examples/performance_test/

#. Start an ArduPilot SITL instance yourself first (see :ref:`sitl_setup` - the old auto-launching
   ``dronekit-sitl`` package this example used to rely on is dead), then run the example passing
   its connection string:

   .. code-block:: bash

       python performance_test.py --connect udp:127.0.0.1:14550

   On the command prompt you should see (something like):

   .. code:: bash

       Connecting to vehicle on: udp:127.0.0.1:14550
       Logging for 30 seconds
       MaxInterval: 0.045  MinInterval: 0.021  Interval: 0.023

   The three numbers update in place on a single line as more acks arrive.

#. You can run the example against a specific connection (simulated or otherwise) by passing the
   :ref:`connection string <get_started_connect_string>` for your vehicle in the ``--connect``
   parameter.


How does it work?
==================

The example sends one test command, then re-sends a new one as soon as the ``COMMAND_ACK`` for
the previous one arrives - so the measured interval is (approximately) the round trip over the
link plus however long the autopilot took to process and ack the command:

.. code-block:: python

    @vehicle.on_message('COMMAND_ACK')
    def listener(self, name, message):
        acktime.update()
        send_testpackets()

``MeasureTime.update()`` timestamps each ack, tracks the running max/min interval since the last
:py:func:`reset` (or program start), and prints them. It deliberately ignores the very first
interval (there is no meaningful "previous" timestamp for the first ack), so the reported numbers
only reflect steady-state round trips.

.. tip::

    This is a link/timing diagnostic, not a template for normal command sending - see
    :doc:`../guide/copter/guided_mode` for the usual way to send commands and wait for results.


Source code
===========

The full source code at documentation build-time is listed below
(`current version on Github <https://github.com/Onikore/dronekit2/blob/main/examples/performance_test/performance_test.py>`_):

.. literalinclude:: ../../examples/performance_test/performance_test.py
    :language: python
