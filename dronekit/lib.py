# Backwards compatibility
# Deliberate compat shim: re-exports everything dronekit/__init__.py's facade exports,
# so it must stay a star-import to automatically track that surface as it changes.
from dronekit import *  # noqa: F403,F405
