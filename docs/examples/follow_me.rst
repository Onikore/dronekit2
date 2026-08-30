.. _example_follow_me:

==================
Example: Follow Me
==================

The *Follow Me* example moves a vehicle to track your position, using location information from a USB GPS attached to your (Linux) laptop.

The source code is a good *starting point* for your own applications. It can be extended to use other 
python language features and libraries (OpenCV, classes, lots of packages etc...)


.. note:: This example can only run on a Linux computer, because it depends on the Linux-only *gpsd* service. 
 
.. warning:: Run this example with caution - be ready to exit follow-me mode by switching the flight mode switch on your RC radio.


Running the example
===================

DroneKit (for Linux) and the vehicle should be set up as described in :ref:`installing_dronekit`.

Once you've done that:

#. Install the *gpsd* service, its command-line clients, and its Python bindings (as shown for
   Ubuntu Linux below - the script does ``import gps``, which ``gpsd``/``gpsd-clients`` alone do
   not provide):

   .. code-block:: bash

       sudo apt-get install gpsd gpsd-clients python3-gps

   You can then plug in a USB GPS and run the "xgps" client to confirm that it is working.
   
   .. note::
   
       If you do not have a USB GPS you can use simulated data by running *dronekit2/examples/follow_me/run-fake-gps.sh*
       (in a separate terminal from where you're running DroneKit-Python). This approach simulates a single location, and so 
       is really only useful for verifying that the script is working correctly.
   

#. Get the DroneKit-Python example source code onto your local machine. The easiest way to do this
   is to clone the **dronekit2** repository from Github. On the command prompt enter:

   .. code-block:: bash

       git clone https://github.com/Onikore/dronekit2.git

#. Navigate to the example folder as shown:

   .. code-block:: bash

       cd dronekit2/examples/follow_me/


#. Start an ArduPilot SITL instance yourself first (see :ref:`sitl_setup` - the old auto-launching
   ``dronekit-sitl`` package this example used to rely on is dead), then run the example passing
   its connection string:

   .. code-block:: bash

       python follow_me.py --connect udp:127.0.0.1:14550

   On the command prompt you should see (something like):

   .. code:: bash

       Connecting to vehicle on: udp:127.0.0.1:14550
       >>> APM:Copter V3.4-dev (e0810c2e)
       >>> Frame: QUAD
       Link timeout, no heartbeat in last 5 seconds
       Basic pre-arm checks
       Waiting for GPS...: None
       ...
       Waiting for GPS...: None
       Taking off!
        Altitude:  0.019999999553
        ...
        Altitude:  4.76000022888
       Reached target altitude
       Going to: LocationGlobalRelative:lat=50.616468333,lon=7.131903333,alt=30
       ...
       Going to: LocationGlobalRelative:lat=50.616468333,lon=7.131903333,alt=30
       Going to: LocationGlobalRelative:lat=50.616468333,lon=7.131903333,alt=30
       User has changed flight modes - aborting follow-me
       Close vehicle object
       Completed
       
   .. note:: 

       The terminal output above was created using simulated GPS data 
       (which is why the same target location is returned every time).
       
       To stop follow-me you can change the vehicle mode or do Ctrl+C
       (on a real flight you can just change the mode switch on your 
       RC transmitter). 
      

#. You can run the example against a specific connection (simulated or otherwise) by passing the :ref:`connection string <get_started_connect_string>` for your vehicle in the ``--connect`` parameter. 

   For example, to connect to SITL running on UDP port 14550 on your local computer:

   .. code-block:: bash

       python follow_me.py --connect 127.0.0.1:14550
   

    
How does it work?
=================

Most of the example should be fairly familiar as it uses the same code as other examples for connecting to the vehicle, 
:ref:`taking off <taking-off>`, and closing the vehicle object. 

The example-specific code is shown below.  All this does is attempt to get a gps socket and read the location in a two second loop. If it is successful it 
reports the value and uses :py:func:`Vehicle.simple_goto <dronekit.Vehicle.simple_goto>` to move to the new position. The loop exits when 
the mode is changed. 

.. code-block:: python

    import gps

    ...

    try:
        # Use the python gps package to access the laptop GPS
        gpsd = gps.gps(mode=gps.WATCH_ENABLE)

        # Arm and take off to an altitude of 5 meters
        arm_and_takeoff(5)

        while True:

            if vehicle.mode.name != "GUIDED":
                print("User has changed flight modes - aborting follow-me")
                break

            # Read the GPS state from the laptop
            next(gpsd)

            # Once we have a valid location (see gpsd documentation) we can start moving our vehicle around
            if (gpsd.valid & gps.LATLON_SET) != 0:
                altitude = 30  # in meters
                dest = LocationGlobalRelative(gpsd.fix.latitude, gpsd.fix.longitude, altitude)
                print(f"Going to: {dest}")

                # A better implementation would only send new waypoints if the position had changed significantly
                vehicle.simple_goto(dest)

                # Send a new target every two seconds
                # For a complete implementation of follow me you'd want adjust this delay
                time.sleep(2)

    except OSError:
        print("Error: gpsd service does not seem to be running, plug in USB GPS or run run-fake-gps.sh")
        sys.exit(1)



Source code
===========

The full source code at documentation build-time is listed below (`current version on github <https://github.com/Onikore/dronekit2/blob/main/examples/follow_me/follow_me.py>`_):

.. include:: ../../examples/follow_me/follow_me.py
    :literal:
