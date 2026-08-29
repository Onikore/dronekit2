.. _quick_start_top:

===========
Quick Start
===========

This topic shows how to quickly install a DroneKit-Python 
*development environment* and run a simple example to get 
vehicle attributes from a *simulated* Copter.


Installation
============

DroneKit-Python is installed from **pip**. You also need a running ArduPilot SITL
simulator to connect to - see :ref:`sitl_setup` for how to build and run it.

.. code-block:: bash

    pip install dronekit2

See :doc:`../develop/installation` for more detailed installation instructions.


Basic "Hello Drone"
===================

With SITL already running in another terminal (see :ref:`sitl_setup`):

.. code-block:: bash

    Tools/autotest/sim_vehicle.py -v ArduCopter --no-rebuild --out=udp:127.0.0.1:14550

the script below imports and calls the :py:func:`connect() <dronekit.connect>` method,
specifying that connection string (``udp:127.0.0.1:14550``). The method returns a
:py:class:`Vehicle <dronekit.Vehicle>` object that we then use to query the attributes.

.. code:: python

    # Import DroneKit-Python
    from dronekit import connect, VehicleMode

    # Connect to the Vehicle (the SITL instance started separately - see sitl_setup).
    connection_string = 'udp:127.0.0.1:14550'
    print("Connecting to vehicle on: %s" % (connection_string,))
    vehicle = connect(connection_string, wait_ready=True)

    # Get some vehicle attributes (state)
    print("Get some vehicle attribute values:")
    print(" GPS: %s" % vehicle.gps_0)
    print(" Battery: %s" % vehicle.battery)
    print(" Last Heartbeat: %s" % vehicle.last_heartbeat)
    print(" Is Armable?: %s" % vehicle.is_armable)
    print(" System status: %s" % vehicle.system_status.state)
    print(" Mode: %s" % vehicle.mode.name)    # settable

    # Close vehicle object before exiting script
    vehicle.close()

    print("Completed")


Copy the text above into a new text file (**hello.py**) and run it in the same way
as you would any other standalone Python script.

.. code-block:: bash

    python hello.py

You should see output along the lines of:

.. code-block:: bash

    Connecting to vehicle on: udp:127.0.0.1:14550
    Get some vehicle attribute values:
     GPS: GPSInfo:fix=3,num_sat=10
     Battery: Battery:voltage=12.587,current=0.0,level=100
     Last Heartbeat: 0.713999986649
     Is Armable?: False
     System status: STANDBY
     Mode: STABILIZE
    Completed

That's it- you've run your first DroneKit-Python script.

Next Steps
==========

* Learn more about :doc:`../develop/index`. 
  This covers development best practices and coding standards,
  and has more information about installation, working with a simulator 
  and setting up a companion computer.
* Read through our step by step :doc:`index` to learn how to connect to your
  vehicle, takeoff, fly, and much more.
* Check out our :doc:`../examples/index`.
