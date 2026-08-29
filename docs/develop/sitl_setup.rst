.. _sitl_setup:

=====================================
Setting up a Simulated Vehicle (SITL)
=====================================

The `SITL (Software In The Loop) <https://ardupilot.org/dev/docs/sitl-simulator-software-in-the-loop.html>`_
simulator allows you to create and test DroneKit-Python apps without a real vehicle (and from the comfort of
your own developer desktop!).

.. note::

    The old ``dronekit-sitl`` pip package (which downloaded and ran pre-built simulator
    binaries) is dead - its binary host returns HTTP 404 and it has not been updated in years.
    This page instead shows how to build and run ArduPilot's own SITL directly, which is
    actively maintained and is exactly what this project's CI uses (see the ``sitl`` job in
    :file:`.github/workflows/ci.yml`).


Building ArduPilot SITL from source
====================================

SITL is built from the `ArduPilot <https://github.com/ArduPilot/ardupilot>`_ source tree using
its ``waf`` build system. This works on Linux natively; on Windows or Mac, use WSL2 or a Linux
VM. The steps below mirror what CI does, pinned to a specific stable release tag for
reproducibility (you can drop ``--branch <tag>`` to build the latest development version
instead):

.. code-block:: bash

    git clone --recurse-submodules --depth 1 --branch Copter-4.6.3 \
        https://github.com/ArduPilot/ardupilot.git
    cd ardupilot

    # Installs the toolchain and Python dependencies waf/sim_vehicle.py need.
    Tools/environment_install/install-prereqs-ubuntu.sh -y

    ./waf configure --board sitl
    ./waf build --target bin/arducopter

Building other vehicle types (ArduPlane, ArduRover, ArduSub, ...) works the same way - swap
the ``--target`` (e.g. ``bin/arduplane``) and the ``-v`` vehicle name used with
``sim_vehicle.py`` below.


Running SITL
============

Launch the simulator with ``sim_vehicle.py``, telling it to output a MAVLink stream over UDP:

.. code-block:: bash

    Tools/autotest/sim_vehicle.py -v ArduCopter --no-rebuild --out=udp:127.0.0.1:14550

By default ``sim_vehicle.py`` also starts *MAVProxy* as a console, which conveniently lets you
fan the connection out to multiple listeners (a DroneKit-Python script *and* a ground station)
at the same time - see :ref:`viewing_uav_on_map` below. Pass ``--no-mavproxy`` if you only want
the raw simulator process (this is what CI does, since there's no interactive console to
attach to there).


Connecting to SITL
===================

DroneKit-Python scripts running on the same computer can connect to the simulation using the
connection string you gave to ``--out`` above:

.. code-block:: python

    vehicle = connect('udp:127.0.0.1:14550', wait_ready=True)

.. _viewing_uav_on_map:

Connecting an additional Ground Station
========================================

You can connect a ground station to an unused port to which messages are being forwarded, using
MAVProxy's ``output add`` command:

.. code:: bash

    output add 127.0.0.1:14551

Then connect DroneKit-Python to one UDP port and a ground station (e.g. *Mission Planner*) to
the other:

.. code-block:: python

    vehicle = connect('127.0.0.1:14550', wait_ready=True)

* `Download and install Mission Planner <http://ardupilot.org/planner/docs/mission-planner-installation.html>`_
* Ensure the selection list at the top right of the Mission Planner screen says *UDP* and then select the **Connect** button next to it.
  When prompted, enter the port number (in this case 14551).

  .. figure:: MissionPlanner_ConnectPort.png
      :width: 50 %

      Mission Planner: Listen Port Dialog

After connecting, vehicle parameters will be loaded into *Mission Planner* and the vehicle is displayed on the map.


.. _sitl_setup_test_connection:

Using SITL (or real hardware) with the test suite
===================================================

The ``dronekit/test`` suite does not launch a simulator itself. Instead, tests that need a
live vehicle read the ``DRONEKIT_TEST_CONNECTION`` environment variable and are skipped (not
failed) if it isn't set. Point it at any connection string accepted by
:py:func:`dronekit.connect`, for example:

.. code-block:: bash

    DRONEKIT_TEST_CONNECTION=tcp:127.0.0.1:5760   # SITL over TCP
    DRONEKIT_TEST_CONNECTION=udp:127.0.0.1:14550  # SITL/companion link over UDP
    DRONEKIT_TEST_CONNECTION=com3                 # real flight controller (Windows)
    DRONEKIT_TEST_CONNECTION=/dev/ttyACM0         # real flight controller (Linux)

.. code-block:: bash

    export DRONEKIT_TEST_CONNECTION=udp:127.0.0.1:14550
    pytest dronekit/test -q -m sitl

Since this connects to *whatever* is at the other end, ``DRONEKIT_TEST_CONNECTION`` works
equally well for a locally-built SITL instance as it does for a real flight controller
plugged in over USB/serial - useful for hardware-in-the-loop testing when you have physical
access to a vehicle. See :file:`dronekit/test/conftest.py` for exactly how the variable is
consumed.
