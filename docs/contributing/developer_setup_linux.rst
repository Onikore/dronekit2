.. _dronekit_development_linux:

===================================
Building DroneKit-Python on Linux
===================================

The setup for *developing* DroneKit-Python on Linux is almost the same as for *using*
DroneKit-Python. We therefore recommend that you start by following the instructions in
:ref:`installing_dronekit`.

When you've got DroneKit and a vehicle (simulated or real) communicating, you can
then build and install your own fork of DroneKit, as discussed below.


Fetch and build DroneKit source
===============================

#. Fork the `dronekit2 <https://github.com/Onikore/dronekit2>`_ project on Github.

#. Run the following commands to clone the project and install it (with its development
   dependencies - pytest, ruff, mypy) in editable mode, in the directory of your choice:

   .. code:: bash

       git clone https://github.com/<your_fork>/dronekit2.git
       cd ./dronekit2
       python3 -m venv .venv
       . .venv/bin/activate
       pip install -e ".[dev]"

   Installing in editable (``-e``) mode means changes to the source tree take effect
   immediately, without needing to reinstall.


Updating DroneKit
=================

Navigate to your local git fork and pull the latest version. Because the package was
installed with ``pip install -e .``, there is nothing further to rebuild:

.. code:: bash

    cd ./<path-to-your-dronekit-fork>/dronekit2
    git pull


Running the test suite
=======================

.. code:: bash

    pytest dronekit/test -q

SITL/hardware-in-the-loop tests are skipped unless ``DRONEKIT_TEST_CONNECTION`` is set -
see :ref:`sitl_setup` for how to point it at a simulator or a real flight controller.
