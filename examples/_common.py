#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
_common.py: Shared connection-string handling for the DroneKit-Python examples.

Every example used to fall back to auto-launching a simulator via the
``dronekit_sitl`` pip package when no ``--connect`` argument was given:

    if not connection_string:
        import dronekit_sitl
        sitl = dronekit_sitl.start_default()
        connection_string = sitl.connection_string()

That package is dead - the S3 host it downloads pre-built simulator binaries
from returns HTTP 404, and it has not been updated in years. There is no
working replacement to auto-launch, so the examples now follow the same
pattern used by dronekit/test/conftest.py: read the connection string from
``--connect`` if given, otherwise from the ``DRONEKIT_TEST_CONNECTION``
environment variable, and fail with an explicit, actionable error if
neither is set - rather than silently trying (and failing) to start a
simulator that no longer exists.

Usage in an example script::

    import os
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from _common import add_connection_argument, get_connection_string

    parser = argparse.ArgumentParser(description='...')
    add_connection_argument(parser)
    args = parser.parse_args()

    connection_string = get_connection_string(args.connect)
"""

import os
import sys

# Same environment variable dronekit/test/conftest.py reads - kept in sync
# deliberately, so there is exactly one way to point *anything* in this
# repository (tests or examples) at a live vehicle.
CONNECTION_ENV_VAR = "DRONEKIT_TEST_CONNECTION"


def add_connection_argument(parser, description=None):
    """Add the standard ``--connect`` argument to an example's ArgumentParser.

    :param parser: an ``argparse.ArgumentParser`` instance.
    :param description: optional text describing what is being connected to,
        substituted into the default help string (e.g. "vehicle").
    """
    what = description or "vehicle"
    parser.add_argument(
        '--connect',
        help=(
            "Connection target string for the {0}. If not specified, the "
            "{1} environment variable is used instead.".format(what, CONNECTION_ENV_VAR)
        ),
    )


def get_connection_string(args_connect):
    """Resolve the connection string an example should use.

    Returns ``args_connect`` if it is set (i.e. ``--connect`` was passed).
    Otherwise falls back to the ``DRONEKIT_TEST_CONNECTION`` environment
    variable. If neither is set, prints an explanatory error and exits the
    process (mirroring how ``dronekit/test/conftest.py`` skips tests that
    need a live vehicle when the same variable is missing).
    """
    connection_string = args_connect or os.environ.get(CONNECTION_ENV_VAR)
    if not connection_string:
        sys.exit(
            "No vehicle connection specified.\n\n"
            "Pass a connection string with --connect <connection-string>, or set the\n"
            "{0} environment variable, e.g.:\n\n"
            "    {0}=tcp:127.0.0.1:5760   (SITL over TCP)\n"
            "    {0}=udp:127.0.0.1:14550  (SITL/companion link over UDP)\n\n"
            "If you don't already have a simulated vehicle running, see\n"
            "docs/develop/sitl_setup.rst for how to build and start ArduPilot SITL\n"
            "(the old auto-launching dronekit-sitl pip package is dead)."
            .format(CONNECTION_ENV_VAR)
        )
    return connection_string
