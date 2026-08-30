=============
Release Notes
=============

This page contains the release notes for dronekit2 ``minor`` and ``major`` releases. See also
`CHANGELOG.md <https://github.com/Onikore/dronekit2/blob/main/CHANGELOG.md>`_ for per-release
detail.

.. note::

    dronekit2 marks releases using the ``major.minor.patch`` release numbering convention, where ``patch`` is used to denote only bug fixes, ``minor`` is used for releases with new features, and ``major`` indicates the release contains significant API changes.

All releases
============

This fork's own releases are listed `on Github here <https://github.com/Onikore/dronekit2/releases>`_.
For releases prior to the fork, see `dronekit-python's release history <https://github.com/dronekit/dronekit-python/releases>`_.

Working with releases
=======================

dronekit2 is not yet published to PyPI (see `the main README
<https://github.com/Onikore/dronekit2#readme>`_ for installing straight from this repository in
the meantime). Once it is, the following commands will work for installing and pinning specific
versions of the ``dronekit2`` package (the import name is unchanged - it's still
``import dronekit``):

.. code-block:: bash

    pip install dronekit2    # Install the latest version
    pip install dronekit2 --upgrade    # Update to the latest version
    pip show dronekit2    # Find out what release you have installed
    pip install dronekit2==3.0.0    # Get a specific release (in this case 3.0.0)

Once releases exist, they'll be listed on the
`dronekit2 project page on PyPI <https://pypi.org/project/dronekit2/#history>`_.

