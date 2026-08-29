.. _installing_dronekit:

===================
Installing DroneKit
===================

DroneKit-Python can be installed on a Linux, Mac OSX, or Windows computer that
has Python 3.9 or later installed and can install Python packages from the Internet.

The PyPI distribution is named ``dronekit2`` (this fork's package name), but the import
name is unchanged - your code still does ``import dronekit``:

.. code-block:: bash

    pip install dronekit2

.. code-block:: python

    import dronekit


**Installation notes:**

* Install ``dronekit2`` with ``pip`` inside a virtual environment:

  .. code-block:: bash

      python3 -m venv .venv
      . .venv/bin/activate
      pip install dronekit2

  On Windows (PowerShell), activate with ``.venv\Scripts\Activate.ps1`` instead.

* On Linux you may need to first install **pip** and the Python development headers:

  .. code-block:: bash

      sudo apt-get install python3-pip python3-dev

  Alternatively, you can use the ``ensurepip`` module to install or upgrade Pip on your system:

  .. code-block:: bash

      python3 -m ensurepip --upgrade

* :doc:`companion-computers` are likely to run on stripped down versions of Linux. Ensure
  you use a variant that ships Python 3.9+ and can install Python packages from the Internet.
* Windows does not come with Python by default. Install it from
  `python.org <https://www.python.org/downloads/windows/>`_ or the Microsoft Store; any current
  CPython 3.9+ distribution works.
* To build and run the test suite from a source checkout instead, see
  :ref:`dronekit_development_linux` / :ref:`dronekit_development_windows`.
