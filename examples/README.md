# DroneKit examples

Each subfolder is a runnable, standalone example script. All of them connect via
`examples/_common.py`'s shared helper: pass `--connect <connection-string>`, or set the
`DRONEKIT_TEST_CONNECTION` environment variable, pointing at either an ArduPilot SITL instance or
a real flight controller. See [`docs/develop/sitl_setup.rst`](../docs/develop/sitl_setup.rst) for
how to start SITL.

For what each example does, see [`docs/examples/index.rst`](../docs/examples/index.rst) - or just
read the script, they're short and commented.

Want to contribute a new example or improve an existing one? See [`../CONTRIBUTING.md`](../CONTRIBUTING.md).
