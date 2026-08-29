=============
Release Notes
=============

This page contains the release notes for DroneKit-Python ``minor`` and ``major`` releases.

.. note::

    DroneKit-Python marks releases using the ``major.minor.patch`` release numbering convention, where ``patch`` is used to denote only bug fixes, ``minor`` is used for releases with new features, and ``major`` indicates the release contains significant API changes.



Latest release
==============

.. include:: github_latest_release.txt

All releases
============

This fork's own releases are listed `on Github here <https://github.com/Onikore/dronekit2/releases>`_.
For releases prior to the fork, see `dronekit-python's release history <https://github.com/dronekit/dronekit-python/releases>`_.

Working with releases
=======================

The following PyPI commands are useful for working with different versions of the ``dronekit2`` package
(the import name is unchanged - it's still ``import dronekit``):

.. code-block:: bash

    pip install dronekit2    # Install the latest version
    pip install dronekit2 --upgrade    # Update to the latest version
    pip show dronekit2    # Find out what release you have installed
    pip install dronekit2==3.0.0    # Get a specific release (in this case 3.0.0)

See the `dronekit2 project page on PyPI <https://pypi.org/project/dronekit2/#history>`_ for a list of all releases available.

