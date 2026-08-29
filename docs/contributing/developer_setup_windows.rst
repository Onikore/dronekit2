.. _dronekit_development_windows:

===================================
Building DroneKit-Python on Windows
===================================

This article shows how to set up an environment for *developing* DroneKit-Python on Windows.


Install DroneKit using a Python command line
=============================================

First set up a command line DroneKit-Python installation, as discussed in :ref:`installing_dronekit`
(any current CPython 3.9+ install from `python.org <https://www.python.org/downloads/windows/>`_
or the Microsoft Store works).


Fetch and build DroneKit source
===============================

#. Fork the `dronekit2 <https://github.com/Onikore/dronekit2>`_ project on Github.

#. Open a command prompt or PowerShell. Run the following commands to clone the project and
   install it (with its development dependencies - pytest, ruff, mypy) in editable mode, in
   the directory of your choice:

   .. code:: bat

       git clone https://github.com/<your_fork>/dronekit2.git
       cd dronekit2
       python -m venv .venv
       .venv\Scripts\activate
       pip install -e ".[dev]"

   Installing in editable (``-e``) mode means changes to the source tree take effect
   immediately, without needing to reinstall.


Updating DroneKit
=================

Navigate to your local git fork and pull the latest version. Because the package was
installed with ``pip install -e .``, there is nothing further to rebuild:

.. code:: bat

    cd <path-to-your-dronekit-fork>\dronekit2
    git pull


Running the test suite
=======================

.. code:: bat

    pytest dronekit/test -q

SITL/hardware-in-the-loop tests are skipped unless ``DRONEKIT_TEST_CONNECTION`` is set -
see :ref:`sitl_setup` for how to point it at a simulator or a real flight controller.
