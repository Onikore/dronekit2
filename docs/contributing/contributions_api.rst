.. _contributing_api:

=======================
Contributing to the API
=======================

This article provides a high level overview of how to contribute changes to the DroneKit-Python source code.

.. tip::

    We highly recommend that changes and ideas are `discussed with the project team
    <https://github.com/Onikore/dronekit2/issues>`_ before starting work!


Submitting changes
==================

Contributors should fork the main `Onikore/dronekit2 <https://github.com/Onikore/dronekit2>`_
repository and contribute changes back to the project ``main`` branch using pull requests

* Changes should be :ref:`tested locally <contributing-test-code>` before submission.
* Changes to the public API should be :ref:`documented <contributing-to-documentation>` (we will provide subediting support!)
* Pull requests should be as small and focussed as possible to make them easier to review.
* Pull requests should be rebased against the main project before submission to make integration easier.



.. _contributing-test-code:

Test code
=========

There are two test suites in DroneKit-Python, both run with `pytest <https://docs.pytest.org/>`_:

* **Unit tests** (:file:`dronekit/test/unit`) — verify code paths that don't need a live vehicle.
* **SITL/hardware-in-the-loop tests** (:file:`dronekit/test/sitl`) — verify real-world code, examples,
  and documentation against an actual connected vehicle (simulated via ArduPilot SITL, or real
  hardware over serial).

Test code should be used to verify new and changed functionality. New tests should:

#. Verify all code paths that code can take.
#. Be concise and straightforward.
#. Be documented.


Setting up local testing
------------------------

Follow the links below to set up a development environment on your Linux or Windows computer.

* :ref:`dronekit_development_linux`
* :ref:`dronekit_development_windows`

The test suite needs the ``dev`` extra (pytest, ruff, mypy), installed with:

.. code:: bash

    pip install -e ".[dev]"

For several tests, you may be required to set an **environment variable**. In your command line, you can set the name of a variable to equal a value using the following invocation, depending on your OS:

.. code:: bash

    export NAME=VALUE      # works on OS X and Linux
    set NAME=VALUE         # works on Windows cmd.exe
    $env:NAME = "VALUE"    # works on Windows Powershell

Unit tests
----------

All new features should be created with accompanying unit tests.

To run the tests and display a summary of the results (on any OS),
navigate to the **dronekit2** folder and enter the following
command on a terminal/prompt:

.. code:: bash

    pytest dronekit/test/unit -q




Writing a new unit test
^^^^^^^^^^^^^^^^^^^^^^^

Create any file named :file:`test_XXX.py` in the :file:`dronekit/test/unit` folder to add it as a
test. Feel free to copy from existing tests to get started. ``pytest`` will pick up any function
named ``test_*`` automatically.

Tests names should be named based on their associated Github issue (for example,
``test_12.py`` for `issue #12 <https://github.com/dronekit/dronekit-python/issues/12>`_,
predating this fork - browse existing test file names in :file:`dronekit/test/sitl` for the
convention)
or describe the functionality covered (for example, ``test_waypoints.py``
for a unit test for the waypoints API).

Use the built-in Python ``assert`` statement to check your code is consistent:

.. note::

    Avoid printing any data from your test!

.. code:: python

    def test_this(the_number_two):
        assert the_number_two > 0, '2 should be greater than zero!'
        assert the_number_two == 2, '2 should equal two!'
        assert the_number_two != 1, '2 should not equal one!'

Please add documentation to each test function describing what behavior it verifies.


SITL / hardware-in-the-loop tests
----------------------------------

Tests under :file:`dronekit/test/sitl` need a *live* vehicle - either ArduPilot SITL (see
:ref:`sitl_setup`) or a real flight controller connected over serial. They read the
``DRONEKIT_TEST_CONNECTION`` environment variable for the connection string to use, and are
*skipped* (not failed) if it isn't set - so it's safe to run the full suite without a vehicle
available.

.. code:: bash

    export DRONEKIT_TEST_CONNECTION=udp:127.0.0.1:14550   # a SITL instance you've started
    pytest dronekit/test -q -m sitl

Every test collected from under :file:`dronekit/test/sitl` is automatically given the ``sitl``
pytest marker (see :file:`dronekit/test/conftest.py`), so ``-m sitl`` selects exactly this
suite. Omit ``DRONEKIT_TEST_CONNECTION`` (or the ``-m sitl`` filter) and these tests are
skipped with an explanatory message instead of failing - this is what CI's default ``test``
job does; a separate ``sitl`` CI job builds and launches ArduPilot SITL itself and then runs
this suite against it (see :file:`.github/workflows/ci.yml`).


Writing a new SITL test
^^^^^^^^^^^^^^^^^^^^^^^^

SITL/hardware-in-the-loop tests should be written or improved whenever:

#. New functionality has been added to encapsulate or abstract older methods of interacting with the API.
#. Example code or documentation has been added.
#. A feature could not be tested by unit tests alone (e.g. timing issues, mode changing, etc.)

You can write a new test by adding (or copying) a file with the naming scheme :file:`test_XXX.py`
to the :file:`dronekit/test/sitl` directory.

Tests names should be named based on their associated Github issue (for example,
``test_12.py`` for `issue #12 <https://github.com/dronekit/dronekit-python/issues/12>`_,
predating this fork)
or describe the functionality covered (for example, ``test_waypoints.py``
for a test of the waypoints API).

Use the ``vehicle`` fixture (defined in :file:`dronekit/test/conftest.py`) to get a connected,
ready :py:class:`Vehicle <dronekit.Vehicle>` for the duration of your test - it connects using
``DRONEKIT_TEST_CONNECTION`` and always closes the connection on teardown:

.. code:: python

    def test_something(vehicle):
        # `vehicle` is already connected with wait_ready=True.
        assert vehicle.mode is not None

        # Test using assert
        ...

Please add documentation to each test function describing what behavior it verifies.
