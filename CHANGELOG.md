# Changelog


## Version 3.0.0

This is the first release of this fork (PyPI package `dronekit2`, source at
[github.com/Onikore/dronekit2](https://github.com/Onikore/dronekit2)), which picks up
maintenance of DroneKit-Python after the upstream `dronekit`/`dronekit-python` project went
dormant after 2.9.2. For the full upgrade guide (with code samples) see
[`docs/about/migrating_v3.rst`](docs/about/migrating_v3.rst).

### What breaks

* **PyPI package renamed to `dronekit2`.** `pip install dronekit` no longer gets you updates;
  install `pip install dronekit2` instead. **The import name is unchanged** - existing code
  still does `import dronekit` / `from dronekit import connect, VehicleMode` with no changes
  required.
* **Python 3.9+ is now required.** Support for Python 2.7 and for Python 3 releases older than
  3.9 has been dropped.
* **No public API names were removed or renamed.** `dronekit/__init__.py` (previously a single
  3200+ line file) is now a thin re-export facade over a real package
  (`errors.py`, `types.py`, `observers.py`, `channels.py`, `locations.py`, `parameters.py`,
  `mission.py`, `gimbal.py`, `vehicle.py`, `connect.py`, ...), but every name that was
  importable from top-level `dronekit` before still is. If you only ever did
  `from dronekit import ...`, this release is a drop-in upgrade.
* The deprecated `status_printer` argument to `connect()` still works exactly as before (still
  deprecated in favor of configuring the `logging` module directly). There has never been a
  separate `errprinter` keyword argument on `connect()` in any released version of this
  library - `ErrprinterHandler` is an internal, unexported implementation detail in
  `dronekit/util.py` and was never part of the public API.
* The external `dronekit-sitl` pip package (auto-downloaded SITL binaries) is dead - its binary
  host no longer serves files. Scripts/tests using `dronekit_sitl.start_default()` need to
  start a SITL instance themselves; see `docs/about/migrating_v3.rst` and
  `dronekit/test/conftest.py` (`DRONEKIT_TEST_CONNECTION`) for the replacement pattern used by
  this project's own examples and tests.

### What's new

* **`CommandInt`**, alongside the existing `Command`: encodes mission items over the MAVLink
  `MISSION_ITEM_INT` wire format (`int32` degrees x 1e7) instead of `Command`'s `float32`
  degrees, giving ~1.11cm resolution at the equator instead of `float32`'s decimetre-scale
  rounding error - useful for precision-landing/survey-style missions. Purely additive;
  `CommandInt.from_command()` converts an existing `Command`.
* **Typed public API.** The package now carries inline type annotations across its public
  surface and ships a `py.typed` marker (PEP 561), so type checkers pick up real types for
  `import dronekit`. `mypy` and `ruff` now run in CI.
* **Test suite migrated from `nose` to `pytest`.** SITL-dependent tests are skipped
  automatically unless `DRONEKIT_TEST_CONNECTION` is set (works against either a local SITL
  instance or a real flight controller over serial).
* **CI migrated to GitHub Actions**, replacing the old Travis/AppVeyor/CircleCI setup; releases
  are published to PyPI via Trusted Publishing (`.github/workflows/release.yml`).
* Internal: the `pymavlink.dialects.v10.ardupilotmega` import used for a few EKF status
  constants was switched to `v20` (the constants are identical between dialects - a no-op for
  behavior, done to standardize on the current dialect going forward).
* Docs rebuilt on the `furo` Sphinx theme (replacing the unmaintained `sphinx_3dr_theme`), with
  stale Python-2-era content rewritten throughout.

### What's fixed

Ten real defects found and fixed with regression tests during this modernization pass
(D1-D10; full detail in the commit history):

* **D1/D2** - `mavudpin_multi` (multi-endpoint UDP-in) had a `write()`/`recv()` bug mixing up
  set indexing, a `str`/`bytes` mismatch, and a silent `UnboundLocalError` on certain paths.
* **D3** - `MAVConnection.stop_threads()` could raise if called before the read/write threads
  had ever been started; now guarded.
* **D4** - audited `mavudpin_multi.address` / `MAVConnection.reset()` fallback behavior; no
  defect found.
* **D5** - all 10 bare `except:` clauses replaced with `except Exception:`, so
  `KeyboardInterrupt`/`SystemExit` are no longer accidentally swallowed.
* **D6** - the two remaining timeout/duration measurements switched to `time.monotonic()`
  (immune to system clock adjustments), matching the rest of the codebase.
* **D7** - the `atexit` cleanup callback now holds only a weak reference to `MAVConnection`,
  so a `Vehicle`/connection that would otherwise be garbage-collected is no longer kept alive
  for the life of the process.
* **D8** - `CommandSequence` now raises loudly instead of silently returning wrong data if
  accessed while a `download()` is still in progress.
* **D9** - `connect()` now closes the underlying `MAVConnection` (sockets/threads) if it fails
  partway through (e.g. a `wait_ready()` timeout), instead of leaking it.
* **D10** - fixed a torn read of `Locations.global_frame`/`global_relative_frame` that could
  observe a partially-updated location.

## Version 2.9.2 (2019-03-18)

### Improvements
* CI integration improvements
* Python3 compatability
* use logging module
* log statustexts
* documentation improvements
* convenience functions added: wait_for, wait_for_armable, arm, disarm, wait_for_mode, wait_for_alt, wait_simple_takeoff
* play_tune method added
* reboot method added
* send_calibrate_gyro, send_calibrate_magnetometer, send_calibrate_magnetometer, send_calibrate_vehicle_level, send_calibrate_barometer all added
* update gimbal orientation from MOUNT_ORIENTATION
* add a still-waiting callback for connect() to provide debug on where the connection is up to
* several new tests added (including, play_tune, reboot and set_attitude_target)

### Cleanup
* flake8 compliance improvements
* test includes pruned
* examples cleaned up

### Bug Fixes
* ignore GCS heartbeats for the purposes of link up
* many!

## Version 2.9.1 (2017-04-21)

### Improvements
* home locatin notifications
* notify ci status to gitter
* basic python 3 support
* isolated logger function so implementers can override
* rename windows installer

### Cleanup
* removed legacy cloud integrations

### Bug Fixes
* fix missing ** operator for pymavlink compatibility

## Version 2.9.0 (2016-08-29)

### Bug Fixes
* MAVConnection stops threads on exit and close
* PX4 Pro flight modes are now properly supported
* go to test now uses correct `global_relative_frame` alt

### Improvements
* Updated pymavlink dependency to v2 from v1 hoping we don't fall behind
  again.

## Version 2.8.0 (2016-07-15)

### Bug Fixes
* Makes sure we are listening to `HOME_LOCATION` message, befor we
  would only set home location if received by waypoints.

## Version 2.7.0 (2016-06-21)

### Improvements
* Adds udpin-multi support

## Version 2.6.0 (2016-06-17)

### Bug Fixes
* Fixes patched mavutil sendfn

## Version 2.5.0 (2016-05-04)

### Improvements
* Catch and display message and attribute errors, then continue
* Improved takeoff example docs
* Deploy docs on successful merge into master (from CircleCI)
* Drone delivery example, explain port to connect
* MicroCGS example now uses SITL
* Make running examples possible on Vagrant

### Bug Fixes
* Mav type for rover was incorrect
* `_is_mode_available` can now handle unrecognized mode codes
* Fix broken links on companion computer page
* Fix infinite loop on channel test



## Version 2.4.0 (2016-02-29)

### Bug Fixes

* Use monotonic clock for all of the internal timeouts and time
  measurements
* Docs fixes


## Version 2.3.0 (2016-02-26)

### New Features

* PX4 compatibility improvements

### Updated Features

* Documentation fixes
* PIP repository improvements
* Mode-setting API improvements
* ardupilot-solo compatibility fixes



## Version 2.2.0 (2016-02-19)

### Bug Fixes

* Splits outbound messages into its own thread.
* Remove of capabilities request on HEARTBEAT listener
* Check if mode_mapping has items before iteration



## Version 2.1.0 (2016-02-16)


### New Features


* Gimbal control attribute
* Autopilot version attribute
* Autopilot capabilities attribute
* Best Practice guide documentation.
* Performance test example (restructured and docs added)

### Updated Features:

Many documentation fixes:

* Restructured documentation with Develop (Concepts) and Guide (HowTo) sections
* Docs separated out "Connection Strings" section.
* Improved test and contribution sections.
* Updated examples and documentation to use DroneKit-Sitl for simulation ("zero setup examples")
* Debugging docs updated with additional libraries.
* Flight Replay example fetches data from TLOG rather than droneshare
* Drone Delivery example now uses strart location for home address.
* Disabled web tests (not currently supported/used)
* Updated copyright range to include changes in 2016

### Bug Fixes

* Numerous minor docs fixes.
* Harmonise nosetest options across each of the integration platforms
* Fix incorrect property marker for airspeed attribute



## Version 2.0.2 (2015-11-30)

### Bug Fixes:

* Updates `requests` dependency to work >=2.5.0


## Version 2.0.0 (2015-11-23)

### New Features:

* Renamed library and package from DroneAPI to DroneKit on pip
* DroneKit Python is now a standalone library and no longer requires use of MAVProxy
* Connect multiple vehicles in one script by creating separate vehicle instances
* Removed NumPy, ProtoBuf as dependencies
* Add MAVLink message listeners using `add_message_listener` methods
* Added `on_attribute` and `on_message` function decorator shorthands
* Added `mount_status`, `system_status`, `ekf_ok`, `is_armable`, `heading`
* Made settable `groundspeed`, `airspeed`
* Moved `dronekit.lib` entries to root package `dronekit`
* Added `parameters.set` and `parameters.get` for fine-tuned parameter access
* `parameters` now observable and iterable (#442)
* Added `last_heartbeat` attribute, updated every event loop with time since last heartbeat (#451)
* Await attributes through `wait_ready` method and `connect` method parameter
* Adds subclassable Vehicle class, used by `vehicle_class` parameter in `connect`

### Updated Features:

* local_connect renamed to connect(), accepting a connection path, link configuration, and timeout settings
* Removed `.set_mavrx_callback`. Use `vehicle.on_message('*', obj)` methods
* Renamed `add_attribute_observer` methods to `add_attribute_listener`, etc. (#420)
* Renamed `wait_init` and `wait_valid` to `wait_ready`
* Split `home_location` is a separate attribute from `commands` waypoint array
* Moved RC channels into `.channels` object (#427)
* Split location information into `local_frame`, `global_frame`, and `global_relative_frame` (and removed `is_relative`) (#445)
* Renamed `flush` to `commands.upload`, as it only impacts waypoints (#276)
* `commands.goto` and `commands.takeoff` renamed to `simple_goto` and `simple_takeoff`

### Bug Fixes:

* `armed` and `mode` attributes updated constantly (#60, #446)
* Parameter setting times out (#12)
* `battery` access can throw exception (#298)
* Vehicle.location reports incorrect is_relative value for Copter (#130)
* Excess arming message when already armed
